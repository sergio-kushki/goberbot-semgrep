"""
Semgrep CLI wrapper with hybrid rules loading
"""

import asyncio
import json
import os
import tempfile
import time
import logging
import yaml
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
import aiohttp
import aiofiles

logger = logging.getLogger("semgrep-runner")


@dataclass
class ScanResult:
    """Result from a Semgrep scan"""
    findings: List[Dict]
    scan_time_ms: int
    rules_used: str
    summary: Dict[str, int]


class SemgrepRunner:
    """Wrapper for Semgrep CLI with hybrid rules loading"""
    
    def __init__(self):
        self.rules_dir = Path("/app/custom-rules")  # Bundled rules in Docker
        self.rules_cache_dir = Path("/tmp/semgrep-rules")
        self.rules_cache_dir.mkdir(exist_ok=True)
        
        # Get rules URL from environment (if provided)
        self.rules_url = os.getenv("CUSTOM_RULES_URL", "").strip()
        
        # Track where rules are loaded from
        self.rules_source = "bundled"
        
        # Rules will be initialized on first use or explicitly via initialize()
        self._initialized = False
        
        # Track remote rules state for auto-update detection
        self.last_etag = None
        self.last_content_length = None
    
    async def initialize(self):
        """Public method to initialize rules (call after event loop is running)"""
        if not self._initialized:
            await self._initialize_rules()
            self._initialized = True
    
    async def _initialize_rules(self):
        """Load rules on startup - bundled rules PLUS optional URL rules"""
        try:
            sources = []
            
            # Always use bundled rules as base
            if self.rules_dir.exists():
                sources.append("bundled:/app/custom-rules")
                logger.info(f"Loaded bundled rules from {self.rules_dir}")
            else:
                logger.error(f"Rules directory not found: {self.rules_dir}")
            
            # Additionally try fetching from URL
            if self.rules_url:
                logger.info(f"Attempting to fetch additional rules from URL: {self.rules_url}")
                success = await self._fetch_rules_from_url()
                if success:
                    sources.append(f"url:{self.rules_url}")
                    logger.info("Successfully loaded additional rules from URL")
                else:
                    logger.warning("Failed to fetch from URL, using only bundled rules")
            
            # Set combined source description
            if len(sources) > 1:
                self.rules_source = " + ".join(sources)
            elif sources:
                self.rules_source = sources[0]
            else:
                self.rules_source = "none"
                
        except Exception as e:
            logger.error(f"Error initializing rules: {e}")
    
    async def _fetch_rules_from_url(self) -> bool:
        """Fetch rules from configured URL and store metadata for change detection"""
        if not self.rules_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.rules_url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Store metadata for change detection
                        self.last_etag = response.headers.get('ETag')
                        self.last_content_length = response.headers.get('Content-Length')
                        
                        logger.debug(f"Downloaded rules metadata: ETag={self.last_etag}, Size={self.last_content_length}")
                        
                        # Save to cache
                        cache_file = self.rules_cache_dir / "downloaded_rules.yaml"
                        async with aiofiles.open(cache_file, 'w') as f:
                            await f.write(content)
                        
                        logger.info(f"Downloaded rules to {cache_file}")
                        return True
                    else:
                        logger.error(f"Failed to fetch rules: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error fetching rules from URL: {e}")
            return False
    
    async def _check_rules_updated(self) -> bool:
        """
        Check if remote rules have been updated since last fetch.
        Uses HTTP HEAD request to check ETag or Content-Length without downloading.
        
        Returns:
            True if rules have changed or if this is the first check, False otherwise
        """
        if not self.rules_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use HEAD request - only fetches headers, not content
                async with session.head(self.rules_url, timeout=5) as response:
                    if response.status == 200:
                        current_etag = response.headers.get('ETag')
                        current_length = response.headers.get('Content-Length')
                        
                        # First time checking - consider it as changed
                        if self.last_etag is None and self.last_content_length is None:
                            logger.info("First rules check - will download")
                            return True
                        
                        # Check if ETag changed (preferred method)
                        if current_etag and self.last_etag:
                            if current_etag != self.last_etag:
                                logger.info(f"Rules updated detected via ETag: {self.last_etag} → {current_etag}")
                                return True
                        
                        # Fallback: check if Content-Length changed
                        if current_length and self.last_content_length:
                            if current_length != self.last_content_length:
                                logger.info(f"Rules update detected via size: {self.last_content_length} → {current_length} bytes")
                                return True
                        
                        # No changes detected
                        logger.debug("No rule updates detected")
                        return False
                    else:
                        logger.warning(f"HEAD request failed: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.warning(f"Error checking for rule updates: {e}")
            return False
    
    def _get_rules_paths(self, rules_file: Optional[str] = None) -> List[Path]:
        """
        Get list of rule paths to use - always includes bundled, plus downloaded if available.
        Returns a list of paths to enable scanning with multiple rule sources.
        """
        paths = []
        
        # Always include bundled rules
        if rules_file == "all":
            # Include all YAML files from bundled directory
            paths.append(self.rules_dir)
        elif rules_file:
            # Specific bundled rule file
            bundled_file = self.rules_dir / rules_file
            if bundled_file.exists():
                paths.append(bundled_file)
        else:
            # Default to security.yaml from bundled
            paths.append(self.rules_dir / "security.yaml")
        
        # Additionally include downloaded rules if available
        downloaded_rules = self.rules_cache_dir / "downloaded_rules.yaml"
        if downloaded_rules.exists() and self.rules_url:
            paths.append(downloaded_rules)
            logger.debug(f"Including downloaded rules from {downloaded_rules}")
        
        return paths
    
    async def scan(
        self,
        code: str,
        language: Optional[str] = None,
        rules_file: Optional[str] = "security.yaml"
    ) -> ScanResult:
        """
        Scan code using Semgrep CLI
        
        Automatically checks for rule updates before scanning to ensure latest rules are used.
        
        Args:
            code: Code to scan
            language: Programming language (for file extension)
            rules_file: Which rules to use
        
        Returns:
            ScanResult with findings and metadata
        """
        # Check if remote rules have been updated before scanning
        if self.rules_url:
            try:
                rules_changed = await self._check_rules_updated()
                if rules_changed:
                    logger.info("Remote rules changed - reloading before scan")
                    await self.reload_rules()
            except Exception as e:
                logger.warning(f"Failed to check for rule updates, continuing with cached rules: {e}")
        
        start_time = time.time()
        
        # Create temporary file with appropriate extension
        file_ext = self._get_file_extension(language, code)
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=file_ext,
            delete=False
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name
        
        try:
            # Get rules paths (can be multiple to merge bundled + downloaded)
            rules_paths = self._get_rules_paths(rules_file)
            
            if not rules_paths:
                raise ValueError("No rules available for scanning")
            
            # Build Semgrep command with multiple --config arguments
            cmd = ["semgrep", "--json", "--quiet"]
            
            # Add each rules path as a separate --config
            for rules_path in rules_paths:
                cmd.extend(["--config", str(rules_path)])
            
            cmd.append(tmp_path)
            
            logger.debug(f"Running: {' '.join(cmd)}")
            logger.debug(f"Using {len(rules_paths)} rule source(s): {[str(p) for p in rules_paths]}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30  # 30 second timeout
            )
            
            # Parse results
            if stdout:
                results = json.loads(stdout.decode())
                findings = self._parse_findings(results)
            else:
                findings = []
            
            if stderr:
                stderr_text = stderr.decode()
                if stderr_text and "error" in stderr_text.lower():
                    logger.warning(f"Semgrep stderr: {stderr_text}")
            
            scan_time_ms = int((time.time() - start_time) * 1000)
            
            # Build summary
            summary = self._build_summary(findings)
            
            # Format rules_used to show all sources
            rules_used_str = " + ".join(str(p) for p in rules_paths)
            
            return ScanResult(
                findings=findings,
                scan_time_ms=scan_time_ms,
                rules_used=rules_used_str,
                summary=summary
            )
            
        except asyncio.TimeoutError:
            logger.error("Semgrep scan timed out")
            raise Exception("Scan timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Semgrep scan failed: {e}")
            raise
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def _get_file_extension(self, language: Optional[str], code: str) -> str:
        """Determine file extension based on language or code analysis"""
        if language:
            ext_map = {
                'javascript': '.js',
                'typescript': '.ts',
                'python': '.py',
                'java': '.java',
                'go': '.go',
                'ruby': '.rb',
                'php': '.php',
                'c': '.c',
                'cpp': '.cpp',
                'csharp': '.cs',
                'rust': '.rs',
            }
            return ext_map.get(language.lower(), '.txt')
        
        # Simple heuristics
        if 'def ' in code or 'import ' in code and ':' in code:
            return '.py'
        if 'function' in code or 'const ' in code or 'let ' in code:
            return '.js'
        if 'public class' in code or 'import java' in code:
            return '.java'
        
        return '.txt'
    
    def _parse_findings(self, semgrep_output: Dict) -> List[Dict]:
        """Parse Semgrep JSON output into simplified findings"""
        findings = []
        
        for result in semgrep_output.get('results', []):
            finding = {
                'rule_id': result.get('check_id', 'unknown'),
                'message': result.get('extra', {}).get('message', ''),
                'severity': result.get('extra', {}).get('severity', 'INFO').upper(),
                'line': result.get('start', {}).get('line', 0),
                'column': result.get('start', {}).get('col', 0),
                'end_line': result.get('end', {}).get('line', 0),
                'code_snippet': result.get('extra', {}).get('lines', ''),
                'metadata': result.get('extra', {}).get('metadata', {})
            }
            
            # Extract CWE if available
            metadata = finding['metadata']
            if 'cwe' in metadata:
                finding['cwe'] = metadata['cwe']
            
            findings.append(finding)
        
        return findings
    
    def _build_summary(self, findings: List[Dict]) -> Dict[str, int]:
        """Build summary of findings by severity"""
        summary = {
            'ERROR': 0,
            'WARNING': 0,
            'INFO': 0,
            'total': len(findings)
        }
        
        for finding in findings:
            severity = finding.get('severity', 'INFO')
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    def _parse_yaml_rules(self, yaml_path: Path) -> Dict:
        """
        Auxiliary function to parse a YAML rules file and extract detailed metadata.
        
        Args:
            yaml_path: Path to the YAML file to parse
            
        Returns:
            Dictionary with file info, rule count, and list of individual rules with their metadata
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                rules_data = yaml.safe_load(f)
            
            rules_list = []
            if rules_data and 'rules' in rules_data:
                for rule in rules_data['rules']:
                    rule_info = {
                        'id': rule.get('id', 'unknown'),
                        'message': rule.get('message', 'No description available'),
                        'severity': rule.get('severity', 'INFO'),
                        'languages': rule.get('languages', []),
                    }
                    
                    # Extract metadata if available
                    metadata = rule.get('metadata', {})
                    if metadata:
                        rule_info['metadata'] = metadata
                        
                        # Extract commonly useful fields from metadata
                        if 'cwe' in metadata:
                            rule_info['cwe'] = metadata['cwe']
                        if 'category' in metadata:
                            rule_info['category'] = metadata['category']
                        if 'confidence' in metadata:
                            rule_info['confidence'] = metadata['confidence']
                    
                    rules_list.append(rule_info)
            
            return {
                'file': yaml_path.name,
                'path': str(yaml_path),
                'rule_count': len(rules_list),
                'rules': rules_list
            }
        except Exception as e:
            logger.error(f"Error parsing YAML file {yaml_path}: {e}")
            return {
                'file': yaml_path.name,
                'path': str(yaml_path),
                'error': str(e),
                'rule_count': 0,
                'rules': []
            }
    
    async def get_rules_info(self) -> List[Dict]:
        """
        Get detailed information about available rules including descriptions, severity, 
        languages, CWE mappings, and other metadata parsed from the YAML files.
        Includes BOTH bundled rules and downloaded rules (if available).
        
        Returns:
            List of dictionaries, one per rule file, each containing:
            - file: filename (e.g., 'security.yaml')
            - path: absolute path to the file
            - source: where rules are loaded from (bundled vs downloaded)
            - rule_count: number of rules in the file
            - rules: list of rule objects with id, message, severity, languages, metadata, etc.
        """
        rules_info = []
        
        try:
            # 1. Always list bundled rules from /app/custom-rules
            if self.rules_dir.is_dir():
                for yaml_file in sorted(self.rules_dir.glob("*.yaml")):
                    file_info = self._parse_yaml_rules(yaml_file)
                    file_info['source'] = 'bundled:/app/custom-rules'
                    rules_info.append(file_info)
            
            # 2. Additionally list downloaded rules if available
            downloaded_rules = self.rules_cache_dir / "downloaded_rules.yaml"
            if downloaded_rules.exists() and self.rules_url:
                file_info = self._parse_yaml_rules(downloaded_rules)
                file_info['source'] = f'url:{self.rules_url}'
                rules_info.append(file_info)
                logger.debug(f"Including downloaded rules from {downloaded_rules}")
                
        except Exception as e:
            logger.error(f"Error getting rules info: {e}")
        
        return rules_info
    
    async def reload_rules(self):
        """Reload rules from configured source (bundled + URL if available)"""
        logger.info("Reloading rules...")
        await self._initialize_rules()
        logger.info(f"Rules reloaded successfully from: {self.rules_source}")


