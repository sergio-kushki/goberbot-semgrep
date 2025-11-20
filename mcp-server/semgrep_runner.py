"""
Semgrep CLI wrapper with hybrid rules loading
"""

import asyncio
import json
import os
import tempfile
import time
import logging
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
    
    async def initialize(self):
        """Public method to initialize rules (call after event loop is running)"""
        if not self._initialized:
            await self._initialize_rules()
            self._initialized = True
    
    async def _initialize_rules(self):
        """Load rules on startup"""
        try:
            if self.rules_url:
                logger.info(f"Attempting to fetch rules from URL: {self.rules_url}")
                success = await self._fetch_rules_from_url()
                if success:
                    self.rules_source = f"url:{self.rules_url}"
                    logger.info("Successfully loaded rules from URL")
                    return
                else:
                    logger.warning("Failed to fetch from URL, falling back to bundled rules")
            
            # Fallback to bundled rules
            if self.rules_dir.exists():
                self.rules_source = "bundled:/app/custom-rules"
                logger.info(f"Using bundled rules from {self.rules_dir}")
            else:
                logger.error(f"Rules directory not found: {self.rules_dir}")
                
        except Exception as e:
            logger.error(f"Error initializing rules: {e}")
    
    async def _fetch_rules_from_url(self) -> bool:
        """Fetch rules from configured URL"""
        if not self.rules_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.rules_url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        
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
    
    def _get_rules_path(self, rules_file: Optional[str] = None) -> Path:
        """Get the path to the rules file to use"""
        # Check if we have downloaded rules
        downloaded_rules = self.rules_cache_dir / "downloaded_rules.yaml"
        if downloaded_rules.exists() and self.rules_url:
            return downloaded_rules
        
        # Fall back to bundled rules
        if rules_file == "all":
            # Return the directory to scan all YAML files
            return self.rules_dir
        
        if rules_file:
            return self.rules_dir / rules_file
        
        return self.rules_dir / "security.yaml"
    
    async def scan(
        self,
        code: str,
        language: Optional[str] = None,
        rules_file: Optional[str] = "security.yaml"
    ) -> ScanResult:
        """
        Scan code using Semgrep CLI
        
        Args:
            code: Code to scan
            language: Programming language (for file extension)
            rules_file: Which rules to use
        
        Returns:
            ScanResult with findings and metadata
        """
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
            # Get rules path
            rules_path = self._get_rules_path(rules_file)
            
            # Run Semgrep
            cmd = [
                "semgrep",
                "--config", str(rules_path),
                "--json",
                "--quiet",
                tmp_path
            ]
            
            logger.debug(f"Running: {' '.join(cmd)}")
            
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
            
            return ScanResult(
                findings=findings,
                scan_time_ms=scan_time_ms,
                rules_used=str(rules_path),
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
    
    async def get_rules_info(self) -> List[Dict]:
        """Get information about available rules"""
        rules_info = []
        
        try:
            rules_path = self._get_rules_path()
            
            if rules_path.is_dir():
                # List all YAML files
                for yaml_file in rules_path.glob("*.yaml"):
                    rules_info.append({
                        'file': yaml_file.name,
                        'path': str(yaml_file),
                        'source': self.rules_source
                    })
            else:
                rules_info.append({
                    'file': rules_path.name,
                    'path': str(rules_path),
                    'source': self.rules_source
                })
        except Exception as e:
            logger.error(f"Error getting rules info: {e}")
        
        return rules_info
    
    async def reload_rules(self):
        """Reload rules from configured source"""
        await self._initialize_rules()

