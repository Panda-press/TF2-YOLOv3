import tensorflow as tf
#-------GPU Setup--------
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)
from tensorflow import keras
from tensorflow.keras import layers
import csv
import numpy as np
from os import walk
import Models
import Loss
from PIL import Image


stage = 3

print("Starting stage: {0}".format(stage))





if stage == 1:
    model = Models.Clasifier_For_Training()


elif stage == 3:

    optimizer = tf.optimizers.RMSprop(1e-4)

    batch_size = 16
    
    model = Models.Yolo(2, 601)

    Loss_Func = Loss.Model_Loss(2, 601)

    def GetYoloPosition(posRatio):
        gridsquare = (8*posRatio)//1
        gridpos = (8*posRatio) - gridsquare
        return int(gridsquare), gridpos

    def Get_Batch_Images(Position):
        path = "D:\Dataset\OpenImage/train/train_0_p"
        images = []
        files = []
        for (dirpath, dirnames, filenames) in walk(path):
            files.append(filenames)

        for file_num in range(Position, Position + batch_size):
            img = Image.open(path+"/{0}".format(files[0][file_num]))
            images.append(np.array(img))

        return tf.cast(tf.convert_to_tensor(np.array(images)), tf.float32)

    def Get_Batch_Targets(Position):
        PATH = "D:\Dataset\OpenImage/annotations\Stage1"
        
        batch_targets = []

        files = []

        for (dirpath, dirnames, filenames) in walk(PATH):
            files.append(filenames)

        for file_num in range(Position, Position + batch_size):
            with open(PATH+"\{0}".format(files[0][file_num])) as csv_file:
                csv_reader = csv.DictReader(csv_file)

                yolo_targets = np.zeros((8, 8, 2+2+601))

                for line in csv_reader:
                    xgridsquare, xgridpos = GetYoloPosition(float(line["xPos"]))
                    ygridsquare, ygridpos = GetYoloPosition(float(line["yPos"]))
                    yolo_targets[xgridsquare, ygridsquare, 0] = xgridpos
                    yolo_targets[xgridsquare, ygridsquare, 1] = ygridpos
                    yolo_targets[xgridsquare, ygridsquare, 2] = float(line["width"])
                    yolo_targets[xgridsquare, ygridsquare, 3] = float(line["height"])
                    bbox_class = None

                    with open("D:\Dataset\OpenImage/annotations/class-descriptions-boxable.csv") as csv_file:
                        class_reader = csv.reader(csv_file, delimiter=",")

                        for class_line in class_reader:
                            line_num = 0
                            if (class_line[0] == line["class"]):
                                bbox_class = line_num
                                break
                            line_num += 1

                    yolo_targets[xgridsquare, ygridsquare, bbox_class+4] = 1
                
                batch_targets.append(yolo_targets)
        
        return tf.cast(tf.convert_to_tensor(batch_targets), tf.float32)
                    
                
    Input = Get_Batch_Images(0)
    Target = Get_Batch_Targets(0)
    # output = model(Input)
    # for i in range(len(output)):
    #     print(output[i])
    #     print(Loss_Func(output[i],Target[i]))


    @tf.function
    def TrainStep(input_images, target_outputs):
        with tf.GradientTape() as gen_tape:
            #outputs = model(input_images)

            loss = tf.constant(0, dtype=tf.float32)
            for i in range(len(input_images)):                
                output = model(tf.convert_to_tensor([input_images[i]]))
                loss += Loss_Func(output[0], target_outputs[i])

            print("loss calculated")
        #for i in range(len(ouputs))
        gradients = gen_tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    for i in range(1,100):
        print(i)
        TrainStep(Input, Target)

    Input = Get_Batch_Images(0)
    Target = Get_Batch_Targets(0)
    output = model(Input)
    print(output[0])
    print(Loss_Func(output[0],Target[0]))    
        
