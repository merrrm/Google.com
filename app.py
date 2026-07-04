import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

# إنشاء مجلد حفظ الملفات إذا لم يكن موجوداً
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# مصفوفة في الذاكرة لتتبع الملفات المرفوعة أثناء التشغيل
received_data = {}

@app.route('/')
def home():
    return "<h1>تطبيق إدارة الملفات عبر الإنترنت يعمل بنجاح!</h1>", 200

@app.route('/api/upload_file', methods=['POST'])
def upload_file():
    """نقطة النهاية لاستقبال الملف الفعلي من تطبيق المرسل"""
    device_name = request.form.get("device_name", "Unknown Device")
    
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "لم يتم إرسال ملف"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "اسم الملف فارغ"}), 400

    # تنظيم الملفات في مجلد خاص باسم الجهاز
    device_folder = os.path.join(UPLOAD_FOLDER, device_name)
    if not os.path.exists(device_folder):
        os.makedirs(device_folder)

    file_path = os.path.join(device_folder, file.filename)
    file.save(file_path)

    # تحديث سجل الذاكرة
    if device_name not in received_data:
        received_data[device_name] = []
    
    if file.filename not in received_data[device_name]:
        received_data[device_name].append(file.filename)
    
    return jsonify({"status": "success", "message": "تم رفع الملف بنجاح إلى Render"}), 200

@app.route('/api/get_devices', methods=['GET'])
def get_devices():
    """جلب قائمة الأجهزة التي قامت برفع ملفات"""
    return jsonify({"devices": list(received_data.keys())}), 200

@app.route('/api/get_files/<device_name>', methods=['GET'])
def get_files(device_name):
    """جلب أسماء الملفات وروابط تحميلها لجهاز معين"""
    files = received_data.get(device_name, [])
    formatted_files = [
        {"file_name": f, "download_url": f"https://google-com-tfu6.onrender.com/api/download/{device_name}/{f}"} 
        for f in files
    ]
    return jsonify({"files": formatted_files}), 200

@app.route('/api/download/<device_name>/<filename>', methods=['GET'])
def download_file(device_name, filename):
    """رابط مباشر لتحميل أو استعراض الملف من قبل تطبيق المشاهدة"""
    return send_from_directory(os.path.join(UPLOAD_FOLDER, device_name), filename)

if __name__ == '__main__':
    # الإعدادات الافتراضية للتشغيل على الاستضافة
    app.run(host='0.0.0.0', port=5000)
