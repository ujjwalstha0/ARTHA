import { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Camera, RefreshCw } from 'lucide-react';

const Step3Verification = ({ data, updateData, submit, prevStep }) => {
    const webcamRef = useRef(null);
    const [imgSrc, setImgSrc] = useState(data.livePhoto || null);

    const capture = useCallback(() => {
        const imageSrc = webcamRef.current.getScreenshot();
        setImgSrc(imageSrc);
        updateData('livePhoto', imageSrc);
    }, [webcamRef, updateData]);

    const retake = () => {
        setImgSrc(null);
        updateData('livePhoto', null);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!imgSrc) {
            alert("Please capture a live photo");
            return;
        }
        submit();
    };

    return (
        <div className="text-center">
            <h3 className="form-section-title">Live Verification</h3>
            <p className="mb-4 text-muted">Please look at the camera to verify your identity.</p>

            <div className="camera-section mb-4">
                {imgSrc ? (
                    <div>
                        <img src={imgSrc} alt="captured" className="captured-image" />
                        <div className="mt-4">
                            <button type="button" onClick={retake} className="btn btn-outline">
                                <RefreshCw size={18} className="mr-2" style={{ marginRight: '0.5rem' }} /> Retake
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="webcam-wrapper">
                        <div className="webcam-container">
                            <Webcam
                                audio={false}
                                ref={webcamRef}
                                screenshotFormat="image/jpeg"
                                width="100%"
                            />
                        </div>
                        <div className="mt-4">
                            <button type="button" onClick={capture} className="btn btn-primary">
                                <Camera size={18} className="mr-2" style={{ marginRight: '0.5rem' }} /> Capture Photo
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <div className="flex justify-between mt-8">
                <button type="button" onClick={prevStep} className="btn btn-outline">Back</button>
                <button type="button" onClick={handleSubmit} className="btn btn-primary btn-lg" disabled={!imgSrc}>
                    Submit Verification
                </button>
            </div>
        </div>
    );
};

export default Step3Verification;
