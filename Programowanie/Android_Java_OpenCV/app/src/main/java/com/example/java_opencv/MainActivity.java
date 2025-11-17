package com.example.java_opencv;

import android.Manifest;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;

import com.felhr.usbserial.UsbSerialDevice;

import org.opencv.android.CameraActivity;
import org.opencv.android.CameraBridgeViewBase;

import org.opencv.android.OpenCVLoader;
import org.opencv.core.Core;

import org.opencv.core.KeyPoint;
import org.opencv.core.Mat;
import org.opencv.core.MatOfKeyPoint;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.features2d.SimpleBlobDetector;
import org.opencv.features2d.SimpleBlobDetector_Params;
import org.opencv.imgproc.Imgproc;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;

import java.util.List;
import java.util.Locale;

import android.content.BroadcastReceiver;

import android.util.Log;

import com.felhr.usbserial.UsbSerialInterface;

import java.io.UnsupportedEncodingException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.Description;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.data.LineData;


public class MainActivity extends CameraActivity {

    CameraBridgeViewBase cameraBridgeViewBase;
    private Mat rgbaFrame;
    private Mat previousGrayFrame;
    private TextView blobCountTextView;
    int blobCount = 0;

    private TextView distanceTextView;
    private TextView startingDistanceTextView;

    private double deformationValue = 0.0;
    private TextView deformationTextView;

    private TextView forceTextView;

    private TextView timeTextView;
    private long startTime;
    private boolean isTimerRunning = false;


    private EditText fileNameEditText;

    boolean applyNegativeEffect = false;
    boolean applyGrayscaleEffect = false;

    private EditText editTextRoiWidth;
    private EditText editTextRoiHeight;

    private TextView MinAreaTextView;


    private TextView MaxAreaTextView;

    private int minArea = 80;
    private int maxArea = 110;

    private int roiWidth;
    private int roiHeight;


    TextView brightnessTextView;
    double brightnessValue = 2.;

    TextView contrastTextView;
    double contrastValue = 2.;

    private LineChart lineChart;

    private List<Double> distanceValues = new ArrayList<>();

    private SharedPreferences sharedPreferences;
    private static final String PREF_NAME = "MyPrefs";
    private static final String BRIGHTNESS_KEY = "brightness";
    private static final String CONTRAST_KEY = "contrast";
    private static final String NEGATIVE_EFFECT_KEY = "negativeEffect";
    private static final String GRAYSCALE_EFFECT_KEY = "grayscaleEffect";
    private static final String MIN_AREA_KEY = "minArea";
    private static final String MAX_AREA_KEY = "maxArea";
    private static final String ROI_WIDTH_KEY = "roiWidth";
    private static final String ROI_HEIGHT_KEY = "roiHeight";

    private List<String> dataEntries = new ArrayList<>();

    private double currentDistance = 0.0;
    private double initialDistance = 0.0;


    private static final String TAG = "MainActivity";

    private UsbManager usbManager;
    private UsbDevice device;
    private UsbSerialDevice serialPort;
    private UsbDeviceConnection connection;
    private final String ACTION_USB_PERMISSION = "com.android.example.USB_PERMISSION";
    private PendingIntent permissionIntent;

    private final BlockingQueue<String> dataQueue = new LinkedBlockingQueue<>();

    private StringBuilder dataBuilder = new StringBuilder();
    private boolean isDecimalPartRead = false;
    private boolean isSpaceBeforeNumber = false;


    // Handler do obsługi odczytanych danych
    private final Handler handler = new Handler(new Handler.Callback() {
        @Override
        public boolean handleMessage(@NonNull Message msg) {
            String data = (String) msg.obj;

            String dataForce = "Siła: " + data;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    forceTextView.setText(dataForce);
                }
            });
            return true;
        }
    });


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        sharedPreferences = getSharedPreferences(PREF_NAME, MODE_PRIVATE);

        getPermission();

        cameraBridgeViewBase = findViewById(R.id.cameraView);

        blobCountTextView = findViewById(R.id.blobCountTextView);

        distanceTextView = findViewById(R.id.distance);
        startingDistanceTextView = findViewById(R.id.startingDistance);

        deformationTextView = findViewById(R.id.deformation);
        forceTextView = findViewById(R.id.force);

        timeTextView = findViewById(R.id.time);

        Button startButton = findViewById(R.id.start);
        Button stopButton = findViewById(R.id.stop);
        Button cleanButton = findViewById(R.id.clean);

        fileNameEditText = findViewById(R.id.fileNameEditText);

        Button saveButton = findViewById(R.id.save);
        Button wykresButton = findViewById(R.id.wykresB);

        CheckBox negativeCheckBox = findViewById(R.id.checkBoxNeg);
        CheckBox grayscaleCheckBox = findViewById(R.id.checkBoxSzar);

        MinAreaTextView = findViewById(R.id.Minarea);
        MaxAreaTextView = findViewById(R.id.Maxarea);


        editTextRoiWidth = findViewById(R.id.editTextRoiWidth);
        editTextRoiHeight = findViewById(R.id.editTextRoiHeight);

        Button changeButton = findViewById(R.id.buttonChangeRoi);

        brightnessTextView = findViewById(R.id.brightness);
        contrastTextView = findViewById(R.id.contrast);
        Button decreaseBrightnessButton = findViewById(R.id.decreasebrightness);
        Button increaseBrightnessButton = findViewById(R.id.incrasebrightness);
        Button decreaseContrastButton = findViewById(R.id.decreasecontrast);
        Button increaseContrastButton = findViewById(R.id.incrasecontrast);

        Button decreaseMinAreaButton = findViewById(R.id.decreaseblobMin);
        Button increaseMixAreaButton = findViewById(R.id.incraseblobMin);
        Button decreaseMaxAreaButton = findViewById(R.id.decreaseblobMax);
        Button increaseMaxAreaButton = findViewById(R.id.incraseblobMax);


        lineChart = findViewById(R.id.lineChartView);

        brightnessValue = sharedPreferences.getFloat(BRIGHTNESS_KEY, 2.0f);
        contrastValue = sharedPreferences.getFloat(CONTRAST_KEY, 2.0f);
        applyNegativeEffect = sharedPreferences.getBoolean(NEGATIVE_EFFECT_KEY, false);
        applyGrayscaleEffect = sharedPreferences.getBoolean(GRAYSCALE_EFFECT_KEY, false);
        minArea = sharedPreferences.getInt(MIN_AREA_KEY,80);
        maxArea = sharedPreferences.getInt(MAX_AREA_KEY,110);
        roiWidth =sharedPreferences.getInt(ROI_WIDTH_KEY,50);
        roiHeight = sharedPreferences.getInt(ROI_HEIGHT_KEY,350);
        editTextRoiWidth.setText(String.valueOf(roiWidth));
        editTextRoiHeight.setText(String.valueOf(roiHeight));

        startTime = 0;

        usbManager = (UsbManager) getSystemService(Context.USB_SERVICE);
        permissionIntent = PendingIntent.getBroadcast(this, 0, new Intent(ACTION_USB_PERMISSION), PendingIntent.FLAG_MUTABLE);
        IntentFilter filter = new IntentFilter(ACTION_USB_PERMISSION);
        registerReceiver(usbReceiver, filter);

        requestPermission();

        updateBrightness();
        updateContrast();

        updateMinArea();
        updateMaxArea();

        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!isTimerRunning) {
                    startTime = System.currentTimeMillis(); // Ustaw bieżący czas jako czas rozpoczęcia
                    isTimerRunning = true; // Rozpocznij pomiar czasu
                    distanceValues.clear(); // Wyczyść tablicę z poprzednich pomiarów
                }
            }
        });

        stopButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Zatrzymaj timer
                isTimerRunning = false;

            }
        });



        saveButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Pobierz wprowadzoną nazwę pliku
                String fileName = fileNameEditText.getText().toString().trim();
                //gdyby zapomniano narysować wykres

                if (fileName.isEmpty()) {
                    // Jeśli nazwa pliku jest pusta, poinformuj użytkownika
                    Toast.makeText(getApplicationContext(), "Wprowadź nazwę pliku", Toast.LENGTH_SHORT).show();
                } else {
                    if (lineChart.getData() != null){
                        saveToFile(fileName);
                        // Konwertuj wykres na bitmapę
                        Bitmap chartBitmap = lineChart.getChartBitmap();
                        saveChartToFile(fileName, chartBitmap);
                    }
                    else{
                        drawChart();
                        saveToFile(fileName);
                        // Konwertuj wykres na bitmapę
                        Bitmap chartBitmap = lineChart.getChartBitmap();
                        saveChartToFile(fileName, chartBitmap);
                    }

                }

            }
        });

        wykresButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                drawChart();
            }
        });

        changeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String roiWidthString = editTextRoiWidth.getText().toString().trim();
                String roiHeightString = editTextRoiHeight.getText().toString().trim();

                if (roiWidthString.isEmpty() && roiHeightString.isEmpty()) {
                    Toast.makeText(getApplicationContext(), "Wprowadź odpowiednie dane", Toast.LENGTH_SHORT).show();
                } else {
                    if(Integer.parseInt(roiWidthString) > 0 && Integer.parseInt(roiHeightString) > 0 && Integer.parseInt(roiWidthString) < 131 && Integer.parseInt(roiHeightString) < 801){
                        roiWidth = Integer.parseInt(roiWidthString);
                        roiHeight = Integer.parseInt(roiHeightString);
                    }else{
                        Toast.makeText(getApplicationContext(), "Wysokość 0-130 Szerokość 0-800", Toast.LENGTH_SHORT).show();
                    }

                }
            }
        });


        decreaseBrightnessButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                decreaseBrightness();
                updateBrightness();
                adjustBrightness(rgbaFrame);
            }
        });

        increaseBrightnessButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                increaseBrightness();
                updateBrightness();
                adjustBrightness(rgbaFrame);
            }
        });

        decreaseContrastButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                decreaseContrast();
                updateContrast();
                adjustContrast(rgbaFrame);
            }
        });

        increaseContrastButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                increaseContrast();
                updateContrast();
                adjustContrast(rgbaFrame);
            }
        });

        decreaseMinAreaButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                decreaseMinArea();
            }
        });

        increaseMixAreaButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                increaseMinArea();
            }
        });


        decreaseMaxAreaButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                decreaseMaxArea();
            }
        });

        increaseMaxAreaButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                increaseMaxArea();
            }
        });

        negativeCheckBox.setChecked(applyNegativeEffect);
        grayscaleCheckBox.setChecked(applyGrayscaleEffect);

        negativeCheckBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                applyNegativeEffect = isChecked;
                savePreferences();
            }
        });

        grayscaleCheckBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                applyGrayscaleEffect = isChecked;
                savePreferences();
            }
        });

        savePreferences();

        cameraBridgeViewBase.setCvCameraViewListener(new CameraBridgeViewBase.CvCameraViewListener2() {
            @Override
            public void onCameraViewStarted(int width, int height) {
                rgbaFrame = new Mat();
            }

            @Override
            public void onCameraViewStopped() {
                rgbaFrame.release();
            }

            @Override
            public Mat onCameraFrame(CameraBridgeViewBase.CvCameraViewFrame inputFrame) {
                rgbaFrame.release();
                rgbaFrame = inputFrame.rgba().clone();


                int frameWidth = inputFrame.rgba().width();
                int frameHeight = inputFrame.rgba().height();

                int roiX = (frameWidth - roiWidth) / 2;
                int roiY = (frameHeight - roiHeight) / 2;

                Rect roi = new Rect(roiX, roiY, roiWidth, roiHeight);

                Mat roiFrame = new Mat(rgbaFrame, roi);

                if(applyNegativeEffect){
                    Imgproc.rectangle(rgbaFrame, roi.tl(), roi.br(), new Scalar(255, 255, 255), 2);
                }
                else{
                    Imgproc.rectangle(rgbaFrame, roi.tl(), roi.br(), new Scalar(0, 0, 0), 2);
                }

                if (applyNegativeEffect) {
                    Core.bitwise_not(rgbaFrame, rgbaFrame);
                }

                if (applyGrayscaleEffect) {
                    Imgproc.cvtColor(rgbaFrame, rgbaFrame, Imgproc.COLOR_RGBA2GRAY);
                    Imgproc.cvtColor(rgbaFrame, rgbaFrame, Imgproc.COLOR_GRAY2RGBA);
                }

                adjustBrightness(rgbaFrame);
                adjustContrast(rgbaFrame);

                Mat grayFrame = new Mat();
                Imgproc.cvtColor(rgbaFrame, grayFrame, Imgproc.COLOR_RGBA2GRAY);

                SimpleBlobDetector_Params params = new SimpleBlobDetector_Params();
                // Ustawienia detektora SimpleBlob
                params.set_minThreshold(10); // Minimalny próg
                params.set_maxThreshold(200); // Maksymalny próg
                params.set_filterByArea(true); // Filtruj po powierzchni
                params.set_minArea(minArea); // Minimalna powierzchnia bloba
                params.set_maxArea(maxArea); // Maksymalna powierzchnia bloba
                params.set_filterByCircularity(true); // Filtruj po okrągłości
                params.set_minCircularity(0.2f); // Minimalna okrągłość
                params.set_filterByConvexity(true); // Filtruj po wypukłości
                params.set_minConvexity(0.8f); // Minimalna wypukłość
                params.set_filterByInertia(true); // Filtruj po inercji
                params.set_minInertiaRatio(0.2f); // Minimalne stosunku inercji

                SimpleBlobDetector detector = SimpleBlobDetector.create(params);
                MatOfKeyPoint keypoints = new MatOfKeyPoint();
                detector.detect(roiFrame, keypoints);

                String czas = " ";

                if (isTimerRunning) {
                    long currentTime = System.currentTimeMillis() - startTime;
                    long seconds = currentTime / 1000;
                    long milliseconds = currentTime % 1000;
                    final String timeText = seconds + "." + String.format(Locale.US, "%03d", milliseconds);
                    czas = timeText;
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            timeTextView.setText(timeText);
                        }
                    });
                }


                List<KeyPoint> keypointsList = keypoints.toList();

                for (KeyPoint point : keypoints.toList()) {
                    int x = (int) (point.pt.x + roiX);
                    int y = (int) (point.pt.y + roiY);
                    int radius = (int) point.size / 2;

                    Imgproc.circle(rgbaFrame, new Point(x, y), radius, new Scalar(0, 255, 0), 1);
                }

                blobCount = keypointsList.size();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        blobCountTextView.setText("Ilość kropek: " + blobCount);
                    }
                });

                if (keypointsList.size() >= 2) {
                    KeyPoint point1 = keypointsList.get(0);
                    KeyPoint point2 = keypointsList.get(1);

                    currentDistance = Math.sqrt(Math.pow(point2.pt.x - point1.pt.x, 2) + Math.pow(point2.pt.y - point1.pt.y, 2));
                    Log.d("currentDistance", "Odległość między blobami: " + currentDistance);

                    final String formattedDistance = String.format(Locale.US, "%.3f", currentDistance);

                    final String distanceText = "Odległość: " + formattedDistance;

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            distanceTextView.setText(distanceText);
                        }
                    });

                    previousGrayFrame = grayFrame.clone();
                }

                if (isTimerRunning && System.currentTimeMillis() - startTime <= 10000) {
                    distanceValues.add(currentDistance);
                }

                if (isTimerRunning && System.currentTimeMillis() - startTime >= 10000 && System.currentTimeMillis() - startTime <= 10200) {
                    initialDistance = calculateAverageDistance(distanceValues);
                    final String initialDistanceText = "Odległość początkowa: " + String.format(Locale.US, "%.3f", initialDistance);
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            startingDistanceTextView.setText(initialDistanceText);
                        }
                    });
                }


                if (isTimerRunning && initialDistance != 0.0 ) {
                    deformationValue = Math.log(currentDistance/ initialDistance);
                    final String deformationText = "Odkształcenie: " + String.format(Locale.US, "%.6f", deformationValue);
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            deformationTextView.setText(deformationText);
                        }
                    });
                }

                saveDataToFile(czas);
                grayFrame.release();
                keypoints.release();
                roiFrame.release();
                return rgbaFrame;
            }
        });


        if (OpenCVLoader.initDebug()){
            cameraBridgeViewBase.enableView();
        }
    }


    private void requestPermission() {
        HashMap<String, UsbDevice> usbDevices = usbManager.getDeviceList();
        if (!usbDevices.isEmpty()) {
            for (Map.Entry<String, UsbDevice> entry : usbDevices.entrySet()) {
                device = entry.getValue();
                usbManager.requestPermission(device, permissionIntent);
            }
        }
    }

    private final BroadcastReceiver usbReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (ACTION_USB_PERMISSION.equals(action)) {
                synchronized (this) {
                    UsbDevice usbDevice = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);

                    if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)) {
                        if (usbDevice != null) {
                            // Otwórz połączenie z urządzeniem
                            connection = usbManager.openDevice(usbDevice);
                            // Uruchom nasłuchiwanie na porcie szeregowym
                            startSerialConnection();
                        }
                    } else {
                        Log.d(TAG, "Permission denied for device " + usbDevice);
                    }
                }
            }
        }
    };

    private void startSerialConnection() {
        if (device != null && connection != null) {
            serialPort = UsbSerialDevice.createUsbSerialDevice(device, connection);
            if (serialPort != null) {
                if (serialPort.open()) {
                    serialPort.setBaudRate(115200);
                    serialPort.setDataBits(UsbSerialInterface.DATA_BITS_8);
                    serialPort.setStopBits(UsbSerialInterface.STOP_BITS_1);
                    serialPort.setParity(UsbSerialInterface.PARITY_NONE);
                    serialPort.setFlowControl(UsbSerialInterface.FLOW_CONTROL_OFF);
                    serialPort.read(mCallback);
                } else {
                    Log.d(TAG, "Port nie został otwarty!");
                }
            } else {
                Log.d(TAG, "Nie znaleziono urządzenia szeregowego!");
            }
        }
    }

    //kodowania: "UTF-8"  "ISO-8859-1"   "US-ASCII"  "UTF-16"


    private UsbSerialInterface.UsbReadCallback mCallback = buffer -> {
        try {
            final String data = new String(buffer, "ISO-8859-1");
            for (char c : data.toCharArray()) {
                if (Character.isDigit(c) || c == '.' || (c == '-' && !isDecimalPartRead)) {
                    dataBuilder.append(c);
                    if (c == '.') {
                        isDecimalPartRead = true;
                    }
                    if (c == ' ') {
                        isSpaceBeforeNumber = true;
                    }
                } else if (c == '\r' || c == '\n') {
                    String finalData = dataBuilder.toString();
                    if (!finalData.isEmpty() && !isSpaceBeforeNumber) {
                        Log.d(TAG, "Dodano " + finalData + " dl:" + finalData.length());
                        handler.obtainMessage(0, finalData).sendToTarget();
                        if(isTimerRunning){
                            dataQueue.offer(finalData);
                        }
                    }
                    dataBuilder.setLength(0);
                    isDecimalPartRead = false;
                    isSpaceBeforeNumber = false;
                }
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
    };



    private void drawChart() {
        if (dataEntries != null) {
            ArrayList<Entry> entries = new ArrayList<>();
            for (String entry : dataEntries) {
                String[] parts = entry.split("\t");
                double deformacja = Double.parseDouble(parts[1]); // Odkształcenie
                double sila = Double.parseDouble(parts[2]); // Siła
                //double czas = Double.parseDouble(parts[0]); // Czas
                entries.add(new Entry((float) deformacja, (float) sila));
                //entries.add(new Entry((float) czas, (float) deformacja));
            }
            LineDataSet dataSet = new LineDataSet(entries, "Siła od Odkształcenia");
            //LineDataSet dataSet = new LineDataSet(entries, "Zmiana odkształcenia w czasie");
            dataSet.setDrawValues(false);
            XAxis xAxis = lineChart.getXAxis();
            xAxis.setTextColor(Color.RED);
            YAxis yAxisLeft = lineChart.getAxisLeft();
            yAxisLeft.setTextColor(Color.RED);
            YAxis yAxisRight = lineChart.getAxisRight();
            yAxisRight.setEnabled(false);
            dataSet.setColor(Color.BLUE);
            LineData lineData = new LineData(dataSet);
            lineChart.setData(lineData);
            Description description = new Description();
            description.setEnabled(false);
            lineChart.setDescription(description);
            lineChart.invalidate();
        }
    }



    private double calculateAverageDistance(List<Double> values) {
        double sum = 0.0;
        for (double value : values) {
            sum += value;
        }
        return sum / values.size();
    }



    private void saveDataToFile(String timeText) {
        String forceData = dataQueue.poll();
        dataQueue.clear();
        if (isTimerRunning && forceData != null) {
            String entry = timeText + "\t" +
                    String.format(Locale.US, "%.6f", deformationValue) + "\t" + forceData;
            dataEntries.add(entry);
        }
    }


    private void saveToFile(String fileName) {
        try {
            File documentsDirectory = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);

            File file = new File(documentsDirectory, "Badanie_" + fileName + ".txt");

            FileOutputStream fos = new FileOutputStream(file);

            for (String entry : dataEntries) {
                fos.write((entry + "\n").getBytes());
            }

            fos.close();

            Toast.makeText(getApplicationContext(), "Pomyślnie zapisano do pliku: " + file.getAbsolutePath(), Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Błąd podczas zapisywania do pliku", Toast.LENGTH_SHORT).show();
        }
    }

    private void saveChartToFile(String fileName, Bitmap chartBitmap) {
        try {
            File documentsDirectory = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);

            File file = new File(documentsDirectory, "Badanie_" + fileName + ".png");

            FileOutputStream fos = new FileOutputStream(file);

            chartBitmap.compress(Bitmap.CompressFormat.PNG, 100, fos);

            fos.close();

            Toast.makeText(getApplicationContext(), "Pomyślnie zapisano do pliku: " + file.getAbsolutePath(), Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "Błąd podczas zapisywania do pliku", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        savePreferences();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        savePreferences();
        if (previousGrayFrame != null) {
            previousGrayFrame.release();
        }
        unregisterReceiver(usbReceiver);
    }

    private void savePreferences() {
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putFloat(BRIGHTNESS_KEY, (float) brightnessValue);
        editor.putFloat(CONTRAST_KEY, (float) contrastValue);
        editor.putBoolean(NEGATIVE_EFFECT_KEY, applyNegativeEffect);
        editor.putBoolean(GRAYSCALE_EFFECT_KEY, applyGrayscaleEffect);
        editor.putInt(MIN_AREA_KEY, minArea);
        editor.putInt(MAX_AREA_KEY, maxArea);
        editor.putInt(ROI_WIDTH_KEY, roiWidth);
        editor.putInt(ROI_HEIGHT_KEY, roiHeight);
        editor.apply();
    }

    private void decreaseBrightness() {
        brightnessValue = Math.max(0.0, brightnessValue - 0.1); // Ograniczenie do minimum 0
    }

    private void increaseBrightness() {
        brightnessValue = Math.min(3.0, brightnessValue + 0.1); // Ograniczenie do maksimum 3.0
    }

    private void decreaseContrast() {
        contrastValue = Math.max(0.1, contrastValue - 0.1); // Ograniczenie do minimum 0.1
    }

    private void increaseContrast() {
        contrastValue = Math.min(3.0, contrastValue + 0.1); // Ograniczenie do maksimum 3.0
    }

    private void updateBrightness() {
        brightnessTextView.setText(String.format(Locale.US, "%.1f", brightnessValue));
    }

    private void updateContrast() {
        contrastTextView.setText(String.format(Locale.US, "%.1f", contrastValue));
    }

    private void decreaseMinArea() {
        minArea = Math.max(0, minArea - 10);
        updateMinArea();
    }

    private void increaseMinArea() {
        if(minArea < maxArea){
            minArea = minArea + 10;
            updateMinArea();
        }

    }

    private void decreaseMaxArea() {
        if(maxArea > minArea){
            maxArea = Math.max(0, maxArea - 10);
            updateMaxArea();
        }

    }

    private void increaseMaxArea() {
        maxArea = maxArea + 10;
        updateMaxArea();
    }

    private void updateMinArea() {
        MinAreaTextView.setText(String.format(Locale.US, "%d", minArea));
    }

    private void updateMaxArea() {
        MaxAreaTextView.setText(String.format(Locale.US, "%d", maxArea));
    }

    private void adjustBrightness(Mat frame) {
        double scaledBrightness = Math.round(brightnessValue * 10.0) / 10.0;
        Mat adjustedFrame = new Mat();
        Core.multiply(frame, new Scalar(scaledBrightness, scaledBrightness, scaledBrightness), adjustedFrame);
        frame.release();
        adjustedFrame.copyTo(frame);
        adjustedFrame.release();
    }

    private void adjustContrast(Mat frame) {
        double scaledContrast = Math.round(contrastValue * 10.0) / 10.0; // Zaokrąglenie do jednego miejsca po przecinku
        Mat adjustedFrame = new Mat();
        Core.multiply(frame, new Scalar(scaledContrast, scaledContrast, scaledContrast), adjustedFrame);
        frame.release();
        adjustedFrame.copyTo(frame);
        adjustedFrame.release();
    }

    @Override
    protected List<? extends CameraBridgeViewBase> getCameraViewList() {
        return Collections.singletonList(cameraBridgeViewBase);
    }

    void getPermission(){
        if(checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.CAMERA}, 102);
        }
    }
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 102 && grantResults.length>0) {
            if(grantResults[0] != PackageManager.PERMISSION_GRANTED){
                getPermission();
            }
        }

    }
}