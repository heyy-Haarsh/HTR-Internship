### InkSight HTR

InkSight HTR is a web-based application designed for the extraction of handwritten text from notebook pages containing ruled lines. The system integrates computer vision techniques for image preprocessing, deep learning for text recognition, and a structured database backend for data management.

---

### Methodology

The application workflow is divided into three primary stages: preprocessing, inference, and data management.

* **Image Preprocessing:** Utilizing OpenCV, raw images undergo a multi-step pipeline to isolate handwritten characters. This includes the removal of horizontal ruled lines, denoising, contrast enhancement, and perspective correction to ensure optimal input for the model.
* **Text Recognition:** The system employs the *WordDetectorNN* model architecture, powered by PyTorch, to perform inference on the preprocessed images and convert extracted word segments into digital text.
* **Data Pipeline:** The application is built using Flask, providing a user-authenticated interface for text extraction. All extracted textual data is persistently stored and managed within an Oracle database hosted via Docker.

---

### Dataset Creation

To support the development of the recognition model, a custom dataset was curated. A proprietary Python-based helper application was developed to facilitate the systematic collection, labeling, and preparation of handwritten data, ensuring the model was trained on representative samples consistent with the application's target use case.

---

### Technical Stack

* **Frontend & Web Framework:** Flask, Bootstrap
* **Deep Learning:** PyTorch
* **Computer Vision:** OpenCV
* **Database:** Oracle
* **Containerization:** Docker

---

Would you like me to refine any of these sections, or are there specific technical details you would like to expand upon?
