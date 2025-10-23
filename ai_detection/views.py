from django.shortcuts import render
from django.http import JsonResponse
from .text_detector import detect_drug_text
from .image_detector import detect_drug_image

def analyze_text(request):
    text = request.GET.get("q", "")
    result = detect_drug_text(text)
    return JsonResponse(result)

def analyze_image(request):
    if request.method == "POST" and request.FILES.get("file"):
        img = request.FILES["file"]
        with open("temp.jpg", "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)
        result = detect_drug_image("temp.jpg")
        return JsonResponse(result)
    return JsonResponse({"error": "No image uploaded"}, status=400)
