#include "Particle.h"

// Enabling system threading to keep the device responsive during network operations:
SYSTEM_THREAD(ENABLED);

// Define the button pin:
const int buttonPin = D4;

// Define the server details:
const char* server = "10.0.2.111";
const int port = 8000;

// Creating a TCPClient instance:
TCPClient client;


void sendPostRequest() {
    // Connecting to the server:
    if (client.connect(server, port)) {
        Serial.println("Connected to server");

        // Constructing the HTTP POST request:
        String postData = "exhibit_info=ExampleExhibitInfo";
        client.println("POST /modified HTTP/1.1");
        client.println("Host: " + String(server));
        client.println("Content-Type: application/x-www-form-urlencoded");
        client.println("Content-Length: " + String(postData.length()));
        client.println();
        client.println(postData);

        // Read and printing the response:
        while (client.connected()) {
            if (client.available()) {
                String line = client.readStringUntil('\n');
                Serial.println(line);
            }
        }

        // Disconnecting from the server:
        client.stop();
        Serial.println("Request sent and connection closed.");
    } else {
        Serial.println("Connection failed.");
    }
}

void setup() {
    // Setting up the button pin as an input with a pull-up resistor
    pinMode(buttonPin, INPUT_PULLUP);

    // Initializing the serial communication and waiting for the port to open:
    Serial.begin(9600);
    while (!Serial) {;}

    Serial.println("Particle Photon setup complete.");
}

void loop() {
    // If the button is pressed, sending a POST request:
    if (digitalRead(buttonPin) == HIGH) {
        sendPostRequest();

        // Delay to prevent spamming:
        delay(10000);
    }
}

/*
cd Particle
particle compile photon2 src --saveTo firmware.bin
particle flash --serial firmware.bin

particle library add HttpClient
*/