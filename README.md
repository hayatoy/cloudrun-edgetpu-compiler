# Serverless Edge TPU Compiler using Cloud Run
A simple REST API which runs Edge TPU compiler on Cloud Run. You can compile your tflite model(s) into Edge TPU model, with a simple HTTPS request, on scalable and managed environment.

## Build and Deploy
The following code will build the container and deploy it to Cloud Run environment.
You may need to modify memory spec if you want to compile larger models. 

```
$ export PROJECTID="{PROJECTID}"
$ gcloud builds submit \
    --tag gcr.io/${PROJECTID}/cloudrun-tpucompiler \
    --project ${PROJECTID}
$ gcloud beta run deploy \
    --image gcr.io/${PROJECTID}/cloudrun-tpucompiler \
    --platform managed \
    --project ${PROJECTID} \
    --concurrency 1 \
    --memory 1024Mi
```

## How to use
You can compile your tflite model to Edge TPU model by REST API. Input model(s) must be on GCS, and output model will be created on GCS.
1. Locate your tflite files to Google Cloud Storage
2. Run following HTTP request
3. You can find the compiled model on GCS

### Single model
```
curl -X POST \
  -F 'gcs_src_uri=gs://MY_BUCKET/inception_v4_299_quant.tflite' \
  -F 'gcs_dst_uri=gs://MY_BUCKET/inception_v4_299_quant_edgetpu.tflite' \
  https://cloudrun-tpucompiler-xxxx.a.run.app/compile
```

### Co-compile models
```
curl -X POST \
  -F 'gcs_src_uri=gs://MY_BUCKET/inception_v4_299_quant.tflite, gs://MY_BUCKET/mobilenet_v1_1.0_224_quant.tflite' \
  -F 'gcs_dst_uri=gs://MY_BUCKET/inception_mobilenet_quant_edgetpu.tflite' \
  https://cloudrun-tpucompiler-xxxx.a.run.app/compile
```