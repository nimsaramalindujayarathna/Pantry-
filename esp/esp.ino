#include <HTTPClient.h>
#include <WiFi.h>
#include "HX711.h"

// Wi-Fi credentials
const char* ssid = "Mobitel";
const char* password = "12345678";

// Firebase details
const char* databaseURL = "https://pantryplus-b207e-default-rtdb.asia-southeast1.firebasedatabase.app"; // Firebase database URL
const char* firebaseAuth = "iF1ikrJWIDietLIhmWefwBRzehKEfnuDKAdovxy7";                                // Firebase authentication token

// HX711 Load Cell pins
#define LOADCELL1_DOUT_PIN  4  // GPIO pin connected to HX711 DOUT for load cell 1
#define LOADCELL1_SCK_PIN   5  // GPIO pin connected to HX711 SCK for load cell 1
#define LOADCELL2_DOUT_PIN  12 // GPIO pin connected to HX711 DOUT for load cell 2
#define LOADCELL2_SCK_PIN   13 // GPIO pin connected to HX711 SCK for load cell 2
#define LOADCELL3_DOUT_PIN  14 // GPIO pin connected to HX711 DOUT for load cell 3
#define LOADCELL3_SCK_PIN   15 // GPIO pin connected to HX711 SCK for load cell 3

// Calibration factors for the load cells
const float CALIBRATION_FACTOR1 = 511; // Replace with your calibration value for load cell 1
const float CALIBRATION_FACTOR2 = 50; // Replace with your calibration value for load cell 2
const float CALIBRATION_FACTOR3 = 1; // Replace with your calibration value for load cell 3

// Create HX711 objects for each load cell
HX711 scale1;
HX711 scale2;
HX711 scale3;

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);  // Reduced delay for faster connection attempts
    Serial.println("Connecting to Wi-Fi...");
  }
  Serial.println("Connected to Wi-Fi!");

  // Initialize HX711 for each load cell
  scale1.begin(LOADCELL1_DOUT_PIN, LOADCELL1_SCK_PIN);
  scale2.begin(LOADCELL2_DOUT_PIN, LOADCELL2_SCK_PIN);
  scale3.begin(LOADCELL3_DOUT_PIN, LOADCELL3_SCK_PIN);

  Serial.println("HX711s initialized!");

  // Set the scale's calibration factors
  scale1.set_scale(CALIBRATION_FACTOR1);
  scale2.set_scale(CALIBRATION_FACTOR2);
  scale3.set_scale(CALIBRATION_FACTOR3);

  Serial.print("Calibration factor for load cell 1 set to: ");
  Serial.println(CALIBRATION_FACTOR1);
  Serial.print("Calibration factor for load cell 2 set to: ");
  Serial.println(CALIBRATION_FACTOR2);
  Serial.print("Calibration factor for load cell 3 set to: ");
  Serial.println(CALIBRATION_FACTOR3);

  // Optional: Tare the scales at startup
  Serial.println("Taring the scales...");
  scale1.tare();
  scale2.tare();
  scale3.tare();
  Serial.println("Scales tared. Ready to measure.");
}

void loop() {
  // Check if all scales are ready and get the weights
  if (scale1.is_ready() && scale2.is_ready() && scale3.is_ready()) {
    float weight1 = scale1.get_units();  // Get weight from load cell 1
    float weight2 = scale2.get_units();  // Get weight from load cell 2
    float weight3 = scale3.get_units();  // Get weight from load cell 3

    Serial.print("Weight from load cell 1: ");
    Serial.println(weight1);
    Serial.print("Weight from load cell 2: ");
    Serial.println(weight2);
    Serial.print("Weight from load cell 3: ");
    Serial.println(weight3);

    // Send data to Firebase
    sendToFirebase(weight1, weight2, weight3);
  } else {
    Serial.println("One or more HX711s not ready. Check wiring.");
  }

  delay(500);  // Reduced delay to get faster readings (0.5 second interval)
}

// Function to send data to Firebase
void sendToFirebase(float weight1, float weight2, float weight3) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Construct Firebase URL for each load cell reading
    String url = String(databaseURL) + "/loadCell.json?auth=" + firebaseAuth;

    // Start the HTTP client
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // Create JSON payload
    String jsonPayload = "{\"loadCell1\":{\"weight\":" + String(weight1) + "},"
                        "\"loadCell2\":{\"weight\":" + String(weight2) + "},"
                        "\"loadCell3\":{\"weight\":" + String(weight3) + "}}";

    // Send PUT request
    int httpResponseCode = http.PUT(jsonPayload);

    // Check HTTP response
    if (httpResponseCode > 0) {
      if (httpResponseCode == 200 || httpResponseCode == 201) {
        Serial.println("Data sent successfully to Firebase.");
      } else {
        Serial.print("Unexpected response code: ");
        Serial.println(httpResponseCode);
      }
    } else {
      Serial.print("Error sending data: ");
      Serial.println(http.errorToString(httpResponseCode).c_str());
    }

    http.end();  // Close the connection
  } else {
    Serial.println("Wi-Fi disconnected!");
  }
}