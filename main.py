import face_recognition
import os, sys
import cv2
import numpy as np
import math
import time

def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear = (1.0 - face_distance) / (range * 2.0)
    
    if face_distance > face_match_threshold:
        return str(round(linear * 100, 2)) + "%"
    else:
        value = (linear + ((1.0 - linear) * math.pow((linear - 0.5)* 2, 0.2))) * 100
        return str(round(value, 2)) + "%"
    

class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True
    
    def __init__(self):
        self.encode_faces()
    
    
    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file('faces/' + image)
            face_encoding = face_recognition.face_encodings(face_image)[0]
            
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        
        print(self.known_face_names)
        
    
    def run_recognition(self):
        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not video_capture.isOpened():
            sys.exit("Video source not found...")
        
        while True:
            success, frame = video_capture.read()
            if success:
                if self.process_current_frame:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB) # changes small frame into RGB format
                    
                    # find all faces
                    self.face_locations = face_recognition.face_locations(rgb_small_frame)
                    self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                    
                    self.face_names = []
                    for face_encoding in self.face_encodings:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        confidence = "???"
                        
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            confidence = face_confidence(face_distances[best_match_index])
                    
                        self.face_names.append(f'{name} ({confidence})')
                
                self.process_current_frame = not self.process_current_frame
                
                # display anotation on the frame
                for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    
                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
                
                cv2.imshow('Face recognition', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()