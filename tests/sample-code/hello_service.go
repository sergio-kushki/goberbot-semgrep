// Package service contains all the services of the project where operations with gateways are performed.
package service

import (
	"context"
	"encoding/json"
	"fmt"

	"bitbucket.org/kushki/usrv-starter-kit-go/tools"
	"bitbucket.org/kushki/usrv-starter-kit-go/types"
	"github.com/aws/aws-lambda-go/events"
)

var (
	refInitializeLambda  = tools.InitializeLambda
	jsonUnmarshallCaller = json.Unmarshal
)

// InitializeHelloService is used to initialize dependencies of service in handler.
func InitializeHelloService(ctx context.Context, event events.APIGatewayProxyRequest) (types.HelloResponse, error) {
	// Initialize lambda.
	conf, logger, err := refInitializeLambda(ctx)
	if err != nil {
		fmt.Println("InitializeHelloService refInitializeLambda error " + err.Error())
		return types.HelloResponse{}, err
	}
	logger.Info("Config Region aws", conf.Region)
	logger.Info("Lambda Hello service", "starting...")

	if err = jsonUnmarshallCaller([]byte(event.Body), &struct{}{}); err != nil {
		logger.Error("InitializeHelloService json unmarshall", err)
		return types.HelloResponse{}, err
	}

	return types.HelloResponse{
		Name: "My First Lambda in kushki",
	}, nil
}