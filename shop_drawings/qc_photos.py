"""
Photo attachment management for QC Inspections and NCR logs.

Handles photo uploads, storage, indexing, and serving for TitanForge QC module.
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filename while preserving extension."""
    import re
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    name = name[:50]  # Limit length
    return f"{name}{ext}"


def _get_photo_dir(base_dir: str, job_code: str) -> str:
    """Get the photos directory for a job."""
    return os.path.join(base_dir, "data", "qc", job_code, "photos")


def _get_photos_index_path(base_dir: str, job_code: str) -> str:
    """Get the path to the photos index file."""
    qc_dir = os.path.join(base_dir, "data", "qc", job_code)
    return os.path.join(qc_dir, "photos_index.json")


def _load_photos_index(base_dir: str, job_code: str) -> Dict:
    """Load the photos index from disk."""
    index_path = _get_photos_index_path(base_dir, job_code)
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"photos": []}
    return {"photos": []}


def _save_photos_index(base_dir: str, job_code: str, index: Dict) -> None:
    """Save the photos index to disk."""
    index_path = _get_photos_index_path(base_dir, job_code)
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)


def _generate_thumbnail(source_path: str, dest_path: str, max_size: int = 200) -> bool:
    """
    Generate a thumbnail for the source image.
    Returns True if successful, False otherwise.
    """
    if not PIL_AVAILABLE:
        return False

    try:
        with Image.open(source_path) as img:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            img.save(dest_path, quality=85)
        return True
    except Exception:
        return False


def save_qc_photo(
    base_dir: str,
    job_code: str,
    record_type: str,
    record_id: str,
    photo_bytes: bytes,
    filename: str,
    caption: str = "",
    uploaded_by: str = ""
) -> Dict:
    """
    Save a photo for a QC record (inspection or NCR).

    Args:
        base_dir: Base directory (combined_calc)
        job_code: Job code
        record_type: "inspection" or "ncr"
        record_id: ID of the inspection or NCR
        photo_bytes: Binary photo data
        filename: Original filename
        caption: Optional caption for the photo
        uploaded_by: User who uploaded (inspector name, etc.)

    Returns:
        Photo metadata dict with: photo_id, filename, original_filename, caption,
        uploaded_by, uploaded_at, file_size, record_type, record_id, thumbnail_path
    """
    # Validate inputs
    if record_type not in ("inspection", "ncr"):
        raise ValueError(f"Invalid record_type: {record_type}")

    # Create photo directory structure
    photo_dir = _get_photo_dir(base_dir, job_code)
    record_photo_dir = os.path.join(photo_dir, record_id)
    os.makedirs(record_photo_dir, exist_ok=True)

    # Generate photo ID and sanitize filename
    photo_id = str(uuid.uuid4())
    sanitized_name = _sanitize_filename(filename)
    photo_filename = f"{photo_id}_{sanitized_name}"
    photo_path = os.path.join(record_photo_dir, photo_filename)

    # Write photo file
    with open(photo_path, 'wb') as f:
        f.write(photo_bytes)

    file_size = len(photo_bytes)
    uploaded_at = datetime.utcnow().isoformat() + "Z"

    # Generate thumbnail
    thumbnail_path = None
    if PIL_AVAILABLE:
        thumb_name = f"{photo_id}_thumb_{sanitized_name}"
        thumb_path = os.path.join(record_photo_dir, "thumbs", thumb_name)
        if _generate_thumbnail(photo_path, thumb_path):
            thumbnail_path = f"photos/{record_id}/thumbs/{thumb_name}"

    # Fallback: use original if no thumbnail
    if not thumbnail_path:
        thumbnail_path = f"photos/{record_id}/{photo_filename}"

    # Create metadata
    metadata = {
        "photo_id": photo_id,
        "filename": photo_filename,
        "original_filename": filename,
        "caption": caption,
        "uploaded_by": uploaded_by,
        "uploaded_at": uploaded_at,
        "file_size": file_size,
        "record_type": record_type,
        "record_id": record_id,
        "thumbnail_path": thumbnail_path
    }

    # Update index
    index = _load_photos_index(base_dir, job_code)
    index["photos"].append(metadata)
    _save_photos_index(base_dir, job_code, index)

    return metadata


def list_qc_photos(
    base_dir: str,
    job_code: str,
    record_type: Optional[str] = None,
    record_id: Optional[str] = None
) -> List[Dict]:
    """
    List photos for QC records.

    Args:
        base_dir: Base directory
        job_code: Job code
        record_type: Filter by "inspection" or "ncr" (optional)
        record_id: Filter by specific record ID (optional)

    Returns:
        List of photo metadata dicts
    """
    index = _load_photos_index(base_dir, job_code)
    photos = index.get("photos", [])

    if record_type:
        photos = [p for p in photos if p.get("record_type") == record_type]

    if record_id:
        photos = [p for p in photos if p.get("record_id") == record_id]

    return photos


def delete_qc_photo(base_dir: str, job_code: str, photo_id: str) -> bool:
    """
    Delete a photo and remove it from the index.

    Args:
        base_dir: Base directory
        job_code: Job code
        photo_id: Photo ID to delete

    Returns:
        True if successful, False otherwise
    """
    index = _load_photos_index(base_dir, job_code)
    photos = index.get("photos", [])

    # Find photo metadata
    photo_meta = None
    for p in photos:
        if p.get("photo_id") == photo_id:
            photo_meta = p
            break

    if not photo_meta:
        return False

    # Delete files
    photo_dir = _get_photo_dir(base_dir, job_code)
    record_id = photo_meta.get("record_id")

    # Delete original
    original_path = os.path.join(photo_dir, record_id, photo_meta.get("filename"))
    if os.path.exists(original_path):
        try:
            os.remove(original_path)
        except OSError:
            pass

    # Delete thumbnail
    thumb_path = photo_meta.get("thumbnail_path")
    if thumb_path and "thumb" in thumb_path:
        full_thumb_path = os.path.join(photo_dir, thumb_path.lstrip("photos/"))
        if os.path.exists(full_thumb_path):
            try:
                os.remove(full_thumb_path)
            except OSError:
                pass

    # Remove from index
    index["photos"] = [p for p in photos if p.get("photo_id") != photo_id]
    _save_photos_index(base_dir, job_code, index)

    return True


def get_photo_path(
    base_dir: str,
    job_code: str,
    record_id: str,
    filename: str
) -> str:
    """
    Get the full file path for serving a photo.

    Args:
        base_dir: Base directory
        job_code: Job code
        record_id: Record ID
        filename: Photo filename

    Returns:
        Full path to the photo file
    """
    photo_dir = _get_photo_dir(base_dir, job_code)
    return os.path.join(photo_dir, record_id, filename)


# HTML/CSS/JS Component for photo uploads
QC_PHOTO_UPLOAD_HTML = """
<div class="qc-photos-container">
    <div id="qc-photos" class="qc-photos-wrapper" data-job="" data-type="" data-record="">
        <!-- Upload area -->
        <div class="photos-upload-section">
            <div class="upload-header">
                <h3 class="upload-title">Photo Attachments</h3>
                <span class="photo-count">(0 photos)</span>
            </div>

            <!-- Drag and drop zone -->
            <div class="photo-dropzone" id="photo-dropzone">
                <div class="dropzone-content">
                    <svg class="dropzone-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <p class="dropzone-text">Drag photos here or click to browse</p>
                    <p class="dropzone-hint">JPG, PNG, WebP (max 10MB each)</p>
                </div>
                <input type="file" id="photo-file-input" multiple accept="image/*" style="display: none;">
            </div>

            <!-- Camera capture (mobile) -->
            <div class="upload-buttons">
                <button class="btn btn-camera" id="photo-camera-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                        <circle cx="12" cy="13" r="4"></circle>
                    </svg>
                    Capture Photo
                </button>
                <button class="btn btn-browse" id="photo-browse-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                        <polyline points="13 2 13 9 20 9"></polyline>
                    </svg>
                    Choose File
                </button>
            </div>

            <!-- Caption input (shown during upload) -->
            <div id="photo-caption-input-wrapper" style="display: none;">
                <input type="text" id="photo-caption-input" class="photo-caption-input" placeholder="Add a caption (optional)">
            </div>

            <!-- Upload progress -->
            <div id="photo-upload-progress" class="photo-upload-progress" style="display: none;">
                <div class="progress-bar">
                    <div class="progress-fill" id="photo-progress-fill"></div>
                </div>
                <span class="progress-text">Uploading...</span>
            </div>
        </div>

        <!-- Photo gallery -->
        <div class="photos-gallery-section">
            <div id="photos-gallery" class="photos-gallery">
                <!-- Photos will be loaded here -->
            </div>
            <div id="photos-empty-state" class="photos-empty-state">
                No photos attached yet
            </div>
        </div>
    </div>

    <!-- Lightbox modal -->
    <div id="photo-lightbox" class="photo-lightbox" style="display: none;">
        <button class="lightbox-close" id="lightbox-close">&times;</button>
        <div class="lightbox-content">
            <button class="lightbox-nav lightbox-prev" id="lightbox-prev">&#10094;</button>
            <img id="lightbox-image" src="" alt="" class="lightbox-image">
            <button class="lightbox-nav lightbox-next" id="lightbox-next">&#10095;</button>
        </div>
        <div class="lightbox-info">
            <p id="lightbox-caption" class="lightbox-caption"></p>
        </div>
    </div>
</div>
"""

QC_PHOTO_STYLES = """
<style>
/* Container */
.qc-photos-container {
    width: 100%;
}

.qc-photos-wrapper {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

/* Upload Section */
.photos-upload-section {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 20px;
}

.upload-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.upload-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #F1F5F9;
}

.photo-count {
    font-size: 14px;
    color: #94A3B8;
}

/* Dropzone */
.photo-dropzone {
    border: 2px dashed #334155;
    border-radius: 8px;
    padding: 32px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #0F172A;
    margin-bottom: 16px;
}

.photo-dropzone:hover {
    border-color: #F6AE2D;
    background: rgba(246, 174, 45, 0.05);
}

.photo-dropzone.drag-over {
    border-color: #F6AE2D;
    background: rgba(246, 174, 45, 0.1);
}

.dropzone-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 12px;
    color: #F6AE2D;
    opacity: 0.7;
}

.dropzone-text {
    margin: 0 0 4px;
    color: #F1F5F9;
    font-size: 16px;
    font-weight: 500;
}

.dropzone-hint {
    margin: 0;
    color: #94A3B8;
    font-size: 14px;
}

/* Upload Buttons */
.upload-buttons {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}

.btn {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s ease;
}

.btn svg {
    width: 18px;
    height: 18px;
}

.btn-camera {
    background: #F6AE2D;
    color: #0F172A;
    flex: 1;
    justify-content: center;
}

.btn-camera:hover {
    background: #FFB84D;
    transform: translateY(-2px);
}

.btn-browse {
    background: #334155;
    color: #F1F5F9;
    flex: 1;
    justify-content: center;
}

.btn-browse:hover {
    background: #475569;
    transform: translateY(-2px);
}

/* Caption Input */
.photo-caption-input-wrapper {
    margin-bottom: 16px;
}

.photo-caption-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #334155;
    border-radius: 6px;
    background: #0F172A;
    color: #F1F5F9;
    font-size: 14px;
    font-family: inherit;
}

.photo-caption-input:focus {
    outline: none;
    border-color: #F6AE2D;
    box-shadow: 0 0 0 3px rgba(246, 174, 45, 0.1);
}

/* Upload Progress */
.photo-upload-progress {
    padding: 12px;
    background: #0F172A;
    border-radius: 6px;
    margin-bottom: 16px;
}

.progress-bar {
    width: 100%;
    height: 6px;
    background: #334155;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-fill {
    height: 100%;
    background: #F6AE2D;
    width: 0%;
    transition: width 0.3s ease;
}

.progress-text {
    font-size: 12px;
    color: #94A3B8;
}

/* Gallery Section */
.photos-gallery-section {
    border-top: 1px solid #334155;
    padding-top: 20px;
}

.photos-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
}

/* Photo Card */
.photo-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
}

.photo-card:hover {
    border-color: #F6AE2D;
    box-shadow: 0 4px 12px rgba(246, 174, 45, 0.1);
    transform: translateY(-4px);
}

.photo-thumbnail {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    cursor: pointer;
    background: #0F172A;
}

.photo-info {
    padding: 12px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.photo-caption {
    margin: 0 0 8px;
    color: #F1F5F9;
    font-size: 13px;
    font-weight: 500;
    word-break: break-word;
    flex: 1;
}

.photo-meta {
    font-size: 11px;
    color: #64748B;
    margin-bottom: 8px;
}

.photo-actions {
    display: flex;
    gap: 6px;
}

.btn-delete {
    padding: 6px 10px;
    background: #7F1D1D;
    color: #FCA5A5;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    flex: 1;
    transition: all 0.2s ease;
}

.btn-delete:hover {
    background: #991B1B;
    color: #FFFFFF;
}

/* Empty State */
.photos-empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #94A3B8;
    font-size: 14px;
}

.photos-empty-state.hidden {
    display: none;
}

/* Lightbox */
.photo-lightbox {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.95);
    z-index: 10000;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.lightbox-close {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(246, 174, 45, 0.1);
    border: 1px solid #F6AE2D;
    color: #F6AE2D;
    width: 40px;
    height: 40px;
    font-size: 28px;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    padding: 0;
}

.lightbox-close:hover {
    background: #F6AE2D;
    color: #0F172A;
}

.lightbox-content {
    position: relative;
    width: 100%;
    max-width: 90vw;
    max-height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.lightbox-image {
    max-width: 100%;
    max-height: 80vh;
    object-fit: contain;
    border-radius: 4px;
}

.lightbox-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(246, 174, 45, 0.1);
    border: 1px solid #F6AE2D;
    color: #F6AE2D;
    width: 40px;
    height: 40px;
    font-size: 24px;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    padding: 0;
}

.lightbox-nav:hover {
    background: #F6AE2D;
    color: #0F172A;
}

.lightbox-prev {
    left: 10px;
}

.lightbox-next {
    right: 10px;
}

.lightbox-info {
    margin-top: 16px;
    text-align: center;
}

.lightbox-caption {
    margin: 0;
    color: #F1F5F9;
    font-size: 14px;
}

/* Responsive */
@media (max-width: 768px) {
    .photos-gallery {
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 12px;
    }

    .upload-buttons {
        gap: 8px;
    }

    .btn {
        padding: 8px 12px;
        font-size: 13px;
    }

    .btn svg {
        width: 16px;
        height: 16px;
    }

    .photo-dropzone {
        padding: 24px 12px;
    }

    .dropzone-icon {
        width: 40px;
        height: 40px;
    }

    .dropzone-text {
        font-size: 14px;
    }

    .dropzone-hint {
        font-size: 12px;
    }

    .lightbox-prev, .lightbox-next {
        width: 36px;
        height: 36px;
        font-size: 20px;
    }
}

@media (max-width: 480px) {
    .photos-gallery {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    }

    .upload-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    .upload-title {
        font-size: 16px;
    }
}
</style>
"""

QC_PHOTO_SCRIPTS = """
<script>
(function() {
    const QCPhotos = {
        currentJobCode: '',
        currentRecordType: '',
        currentRecordId: '',
        photos: [],
        lightboxIndex: 0,
        maxFileSize: 10 * 1024 * 1024,

        init: function(jobCode, recordType, recordId) {
            this.currentJobCode = jobCode;
            this.currentRecordType = recordType;
            this.currentRecordId = recordId;

            const wrapper = document.getElementById('qc-photos');
            if (wrapper) {
                wrapper.dataset.job = jobCode;
                wrapper.dataset.type = recordType;
                wrapper.dataset.record = recordId;
            }

            this.setupEventListeners();
            this.loadPhotos();
        },

        setupEventListeners: function() {
            const dropzone = document.getElementById('photo-dropzone');
            const fileInput = document.getElementById('photo-file-input');
            const cameraBtn = document.getElementById('photo-camera-btn');
            const browseBtn = document.getElementById('photo-browse-btn');
            const captionInput = document.getElementById('photo-caption-input');
            const lightboxClose = document.getElementById('lightbox-close');
            const lightboxPrev = document.getElementById('lightbox-prev');
            const lightboxNext = document.getElementById('lightbox-next');
            const lightbox = document.getElementById('photo-lightbox');

            // Dropzone
            if (dropzone) {
                dropzone.addEventListener('click', () => fileInput.click());
                dropzone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    dropzone.classList.add('drag-over');
                });
                dropzone.addEventListener('dragleave', () => {
                    dropzone.classList.remove('drag-over');
                });
                dropzone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    dropzone.classList.remove('drag-over');
                    this.handleFiles(e.dataTransfer.files);
                });
            }

            // File input
            if (fileInput) {
                fileInput.addEventListener('change', (e) => {
                    this.handleFiles(e.target.files);
                });
            }

            // Camera button
            if (cameraBtn) {
                cameraBtn.addEventListener('click', () => {
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = 'image/*';
                    input.capture = 'environment';
                    input.addEventListener('change', (e) => {
                        this.handleFiles(e.target.files);
                    });
                    input.click();
                });
            }

            // Browse button
            if (browseBtn) {
                browseBtn.addEventListener('click', () => {
                    fileInput.click();
                });
            }

            // Lightbox
            if (lightboxClose) {
                lightboxClose.addEventListener('click', () => {
                    lightbox.style.display = 'none';
                });
            }

            if (lightbox) {
                lightbox.addEventListener('click', (e) => {
                    if (e.target === lightbox) {
                        lightbox.style.display = 'none';
                    }
                });
            }

            if (lightboxPrev) {
                lightboxPrev.addEventListener('click', () => {
                    this.lightboxIndex = (this.lightboxIndex - 1 + this.photos.length) % this.photos.length;
                    this.showLightboxImage();
                });
            }

            if (lightboxNext) {
                lightboxNext.addEventListener('click', () => {
                    this.lightboxIndex = (this.lightboxIndex + 1) % this.photos.length;
                    this.showLightboxImage();
                });
            }
        },

        handleFiles: function(files) {
            const fileArray = Array.from(files);
            const validFiles = fileArray.filter(file => {
                if (!file.type.startsWith('image/')) {
                    alert('Please select image files only');
                    return false;
                }
                if (file.size > this.maxFileSize) {
                    alert(`File ${file.name} is too large (max 10MB)`);
                    return false;
                }
                return true;
            });

            if (validFiles.length === 0) return;

            const captionWrapper = document.getElementById('photo-caption-input-wrapper');
            const captionInput = document.getElementById('photo-caption-input');

            if (captionWrapper && validFiles.length === 1) {
                captionWrapper.style.display = 'block';
                captionInput.value = '';
                captionInput.focus();
            }

            validFiles.forEach((file, index) => {
                setTimeout(() => {
                    this.uploadPhoto(file);
                }, index * 300);
            });
        },

        uploadPhoto: function(file) {
            const caption = document.getElementById('photo-caption-input').value || '';
            const formData = new FormData();
            formData.append('job_code', this.currentJobCode);
            formData.append('record_type', this.currentRecordType);
            formData.append('record_id', this.currentRecordId);
            formData.append('photo', file);
            formData.append('caption', caption);

            const progressWrapper = document.getElementById('photo-upload-progress');
            const progressFill = document.getElementById('photo-progress-fill');

            if (progressWrapper) {
                progressWrapper.style.display = 'block';
            }

            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    if (progressFill) {
                        progressFill.style.width = percentComplete + '%';
                    }
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    if (progressWrapper) {
                        progressWrapper.style.display = 'none';
                    }
                    const captionWrapper = document.getElementById('photo-caption-input-wrapper');
                    if (captionWrapper) {
                        captionWrapper.style.display = 'none';
                    }
                    this.loadPhotos();
                } else {
                    alert('Failed to upload photo');
                }
            });

            xhr.addEventListener('error', () => {
                alert('Upload error');
            });

            xhr.open('POST', '/api/qc/photos/upload');
            xhr.send(formData);
        },

        loadPhotos: function() {
            const params = new URLSearchParams({
                job_code: this.currentJobCode,
                record_type: this.currentRecordType,
                record_id: this.currentRecordId
            });

            fetch(`/api/qc/photos?${params}`)
                .then(r => r.json())
                .then(data => {
                    this.photos = data.photos || [];
                    this.renderPhotos();
                })
                .catch(err => console.error('Failed to load photos:', err));
        },

        renderPhotos: function() {
            const gallery = document.getElementById('photos-gallery');
            const emptyState = document.getElementById('photos-empty-state');
            const count = document.querySelector('.photo-count');

            if (!gallery) return;

            gallery.innerHTML = '';

            if (this.photos.length === 0) {
                if (emptyState) emptyState.classList.remove('hidden');
                if (count) count.textContent = '(0 photos)';
                return;
            }

            if (emptyState) emptyState.classList.add('hidden');
            if (count) count.textContent = `(${this.photos.length} photo${this.photos.length !== 1 ? 's' : ''})`;

            this.photos.forEach((photo, index) => {
                const card = document.createElement('div');
                card.className = 'photo-card';

                const thumbnailUrl = `/api/qc/photos/${this.currentJobCode}/${photo.record_id}/${photo.thumbnail_path.split('/').pop()}`;
                const originalUrl = `/api/qc/photos/${this.currentJobCode}/${photo.record_id}/${photo.filename}`;

                card.innerHTML = `
                    <img src="${thumbnailUrl}" alt="${photo.original_filename}" class="photo-thumbnail"
                         data-index="${index}" data-url="${originalUrl}">
                    <div class="photo-info">
                        ${photo.caption ? `<p class="photo-caption">${this.escapeHtml(photo.caption)}</p>` : ''}
                        <div class="photo-meta">
                            ${photo.uploaded_by ? `By: ${this.escapeHtml(photo.uploaded_by)}` : ''}
                        </div>
                        <div class="photo-actions">
                            <button class="btn-delete" data-photo-id="${photo.photo_id}">Delete</button>
                        </div>
                    </div>
                `;

                const thumbnail = card.querySelector('.photo-thumbnail');
                thumbnail.addEventListener('click', () => {
                    this.lightboxIndex = index;
                    this.showLightbox();
                });

                const deleteBtn = card.querySelector('.btn-delete');
                deleteBtn.addEventListener('click', () => {
                    if (confirm('Delete this photo?')) {
                        this.deletePhoto(photo.photo_id);
                    }
                });

                gallery.appendChild(card);
            });
        },

        showLightbox: function() {
            const lightbox = document.getElementById('photo-lightbox');
            if (lightbox) {
                lightbox.style.display = 'flex';
                this.showLightboxImage();
            }
        },

        showLightboxImage: function() {
            const photo = this.photos[this.lightboxIndex];
            if (!photo) return;

            const image = document.getElementById('lightbox-image');
            const caption = document.getElementById('lightbox-caption');

            const imageUrl = `/api/qc/photos/${this.currentJobCode}/${photo.record_id}/${photo.filename}`;
            if (image) image.src = imageUrl;
            if (caption) caption.textContent = photo.caption || photo.original_filename;
        },

        deletePhoto: function(photoId) {
            fetch('/api/qc/photos/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_code: this.currentJobCode,
                    photo_id: photoId
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    this.loadPhotos();
                } else {
                    alert('Failed to delete photo');
                }
            })
            .catch(err => console.error('Delete error:', err));
        },

        escapeHtml: function(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
    };

    window.QCPhotos = QCPhotos;
})();
</script>
"""


def get_photo_component_bundle() -> Dict[str, str]:
    """
    Get a complete bundle of CSS, JS, and HTML for photo upload component.

    Returns:
        Dict with 'html', 'css', and 'js' keys containing complete code
    """
    return {
        "html": QC_PHOTO_UPLOAD_HTML,
        "css": QC_PHOTO_STYLES,
        "js": QC_PHOTO_SCRIPTS
    }


def inject_photo_component(html_content: str, job_code: str, record_type: str, record_id: str) -> str:
    """
    Inject the photo component into HTML content with initialization.

    Args:
        html_content: Original HTML template content
        job_code: Job code for this record
        record_type: "inspection" or "ncr"
        record_id: ID of the record

    Returns:
        HTML content with injected component and initialization
    """
    bundle = get_photo_component_bundle()

    # Replace placeholders in component
    component_html = bundle["html"].replace("data-job=\"\"", f'data-job="{job_code}"')
    component_html = component_html.replace("data-type=\"\"", f'data-type="{record_type}"')
    component_html = component_html.replace("data-record=\"\"", f'data-record="{record_id}"')

    # Add initialization script
    init_script = f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        if (window.QCPhotos) {{
            window.QCPhotos.init('{job_code}', '{record_type}', '{record_id}');
        }}
    }});
    </script>
    """

    # Combine all parts
    complete_content = (
        bundle["css"] +
        component_html +
        bundle["js"] +
        init_script
    )

    return complete_content
