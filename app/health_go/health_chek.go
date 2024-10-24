package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"time"

	"app/core/middleware"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"github.com/streadway/amqp"
)

type HealthStatus struct {
	Status string     `json:"status"`
	Checks []HealthCheck `json:"checks"`
	Data   HealthData `json:"data"`
}

type HealthCheck struct {
	Name   string      `json:"name"`
	Status string      `json:"status"`
	Data   interface{} `json:"data"`
}

type HealthData struct {
	From   string `json:"from"`
	Status string `json:"status"`
}

// MongoDB readiness check
func checkMongoDB() HealthCheck {
	uri := os.Getenv("MONGO_URI")
	client, err := mongo.NewClient(options.Client().ApplyURI(uri))
	if err != nil {
		return HealthCheck{Name: "MongoDB Check", Status: "DOWN", Data: err.Error()}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err = client.Connect(ctx)
	if err != nil {
		return HealthCheck{Name: "MongoDB Check", Status: "DOWN", Data: err.Error()}
	}

	defer client.Disconnect(ctx)
	return HealthCheck{Name: "MongoDB Check", Status: "UP", Data: map[string]string{"status": "READY"}}
}

// RabbitMQ readiness check
func checkRabbitMQ() HealthCheck {
	rabbitMQHost := os.Getenv("RABBITMQ_HOST")
	conn, err := amqp.Dial(rabbitMQHost)
	if err != nil {
		return HealthCheck{Name: "RabbitMQ Check", Status: "DOWN", Data: err.Error()}
	}
	defer conn.Close()

	return HealthCheck{Name: "RabbitMQ Check", Status: "UP", Data: map[string]string{"status": "ALIVE"}}
}

// Health endpoint handler
func healthHandler(c *gin.Context) {
	healthStatus := HealthStatus{
		Status: "UP",
		Checks: []HealthCheck{
			checkMongoDB(),
			checkRabbitMQ(),
		},
		Data: HealthData{
			From:   time.Now().Format(time.RFC3339),
			Status: "ALIVE",
		},
	}

	c.JSON(http.StatusOK, healthStatus)
}

func main() {
	router := gin.Default()

	// Health check route
	router.GET("/health", healthHandler)

	// Add other routes here

	// Start the server
	router.Run(":8080")
}
