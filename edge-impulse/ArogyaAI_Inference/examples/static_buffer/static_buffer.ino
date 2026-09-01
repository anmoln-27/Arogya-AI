/* Includes ---------------------------------------------------------------- */
#include <Arogya AI_Inference.h>

/**
 * @brief      Arduino setup function
 */
void setup()
{
    // put your setup code here, to run once:
    Serial.begin(115200);
    // comment out the below line to cancel the wait for USB serial connection
    while (!Serial);

    Serial.println("Edge Impulse Inferencing Demo");
}

/**
 * @brief      Arduino main function
 */
void loop()
{
    ei_printf("Edge Impulse standalone inferencing (Arduino)\n");

    if (EI_CLASSIFIER_RAW_SAMPLE_COUNT <= 0) {
        ei_printf("ERR: EI_CLASSIFIER_RAW_SAMPLE_COUNT is <= 0\n");
        return;
    }

    /* 
     * To run the classifier, you need a signal_t structure.
     * This setup is for stationary data (static buffer).
     */
    static float features[] = {
        // Copy a raw sample from the Edge Impulse Studio here
        // (e.g. from the 'Live classification' or 'Data acquisition' tab)
    };

    if (sizeof(features) / sizeof(float) != EI_CLASSIFIER_RAW_SAMPLE_COUNT) {
        ei_printf("ERR: The size of your 'features' array (%d) should match EI_CLASSIFIER_RAW_SAMPLE_COUNT (%d)\n",
            sizeof(features) / sizeof(float), EI_CLASSIFIER_RAW_SAMPLE_COUNT);
        return;
    }

    signal_t signal;
    int err = numpy::signal_from_buffer(features, EI_CLASSIFIER_RAW_SAMPLE_COUNT, &signal);
    if (err != 0) {
        ei_printf("ERR: Failed to create signal from buffer (%d)\n", err);
        return;
    }

    // Run the classifier
    ei_impulse_result_t result = { 0 };

    err = run_classifier(&signal, &result, false);
    if (err != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", err);
        return;
    }

    // Print the predictions
    ei_printf("Predictions (DSP: %d ms., Classification: %d ms., Anomaly: %d ms.): \n",
        result.timing.dsp, result.timing.classification, result.timing.anomaly);
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        ei_printf("    %s: %.5f\n", result.classification[ix].label, result.classification[ix].value);
    }
#if EI_CLASSIFIER_HAS_ANOMALY == 1
    ei_printf("    anomaly score: %.3f\n", result.anomaly);
#endif

    delay(2000);
}

/**
 * @brief      Printf function uses vsnprintf and prints to Serial
 */
void ei_printf(const char *format, ...) {
    static char print_buf[1024] = { 0 };

    va_list args;
    va_start(args, format);
    int r = vsnprintf(print_buf, sizeof(print_buf), format, args);
    va_end(args);

    if (r > 0) {
        Serial.print(print_buf);
    }
}
