package utils

import (
	"log"

	"github.com/streadway/amqp"
)

func ConnectToRabbitMQ() (*amqp.Channel, error) {
	conn, err := amqp.Dial("amqp://guest:guest@rabbitmq_container:5672/")
	if err != nil {
		return nil, err
	}

	ch, err := conn.Channel()
	if err != nil {
		return nil, err
	}

	return ch, nil
}

func PublishLogMessage(ch *amqp.Channel, logMessage string) error {
	err := ch.Publish(
		"",           // exchange
		"logs_queue", // routing key (nombre de la cola)
		false,        // mandatory
		false,        // immediate
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(logMessage),
		})
	if err != nil {
		log.Printf("Error publicando mensaje: %s", err)
		return err
	}

	return nil
}
