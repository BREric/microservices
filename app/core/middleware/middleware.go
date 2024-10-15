package middleware

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
	"github.com/streadway/amqp"
)

var jwtSecret = []byte("your_secret_key")

type LogRequest struct {
	AppName     string `json:"app_name"`
	LogType     string `json:"log_type"`
	Module      string `json:"module"`
	Summary     string `json:"summary"`
	Description string `json:"description"`
}

func SendLog(logReq LogRequest) error {
	jsonData, err := json.Marshal(logReq)
	if err != nil {
		return err
	}

	conn, err := amqp.Dial("amqp://guest:guest@rabbitmq:5672/")
	if err != nil {
		return err
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return err
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"logs_queue", // name
		true,         // durable
		false,        // delete when unused
		false,        // exclusive
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		return err
	}

	err = ch.Publish(
		"",          // exchange
		q.Name,      // routing key
		false,       // mandatory
		false,       // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        jsonData,
		},
	)
	if err != nil {
		return err
	}

	return nil
}

func LoggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		startTime := time.Now()

		path := c.Request.URL.Path
		method := c.Request.Method
		ip := c.ClientIP()

		c.Next()

		statusCode := c.Writer.Status()
		latency := time.Since(startTime)
		userAgent := c.Request.UserAgent()

		logReq := LogRequest{
			AppName:     "MyGoApp",
			LogType:     "INFO",
			Module:      "LoggingMiddleware",
			Summary:     fmt.Sprintf("Solicitud %s %s", method, path),
			Description: fmt.Sprintf("Método: %s, IP: %s, Estado: %d, Latencia: %s, User-Agent: %s", method, ip, statusCode, latency, userAgent),
		}

		err := SendLog(logReq)
		if err != nil {
			log.Println("Error sending log:", err)
		}

		log.Printf("[%d] %s %s %s %s in %v\n", statusCode, method, path, ip, userAgent, latency)
	}
}

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Bearer token required"})
			c.Abort()
			return
		}

		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return jwtSecret, nil
		})

		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
			c.Abort()
			return
		}

		if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
			if exp, ok := claims["exp"].(float64); ok {
				if time.Now().Unix() > int64(exp) {
					c.JSON(http.StatusUnauthorized, gin.H{"error": "token expired"})
					c.Abort()
					return
				}
			}

			if username, ok := claims["username"].(string); !ok || username == "" {
				c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token: username missing"})
				c.Abort()
				return
			}

			c.Set("userClaims", claims)

			c.Next()
		} else {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token claims"})
			c.Abort()
			return
		}
	}
}
