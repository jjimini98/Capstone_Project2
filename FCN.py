# -*- coding: utf-8 -*-

from __future__ import print_function

import pdb

import tensorflow as tf
import numpy as np
import datetime

import TensorflowUtils as utils
import read_MITSceneParsingData as scene_parsing
import BatchDatsetReader as dataset

# 학습에 필요한 설정값들을 tf.flag.FLAGS로 지정합니다.
FLAGS = tf.flags.FLAGS
tf.flags.DEFINE_integer("batch_size", "2", "batch size for training")
tf.flags.DEFINE_string("logs_dir", "logs/", "path to logs directory")
tf.flags.DEFINE_string("data_dir", "Data_zoo/MIT_SceneParsing/", "path to dataset")
tf.flags.DEFINE_float("learning_rate", "5e-5", "Learning rate for Adam Optimizer")
tf.flags.DEFINE_string("model_dir", "Model_zoo/", "Path to vgg model mat")
tf.flags.DEFINE_string('mode', "train", "Mode train/ visualize")

# VGG-19의 파라미터가 저장된 mat 파일(MATLAB 파일)을 받아올 경로를 지정합니다.
MODEL_URL = 'http://www.vlfeat.org/matconvnet/models/beta16/imagenet-vgg-verydeep-19.mat'

# 학습에 필요한 설정값들을 지정합니다.
MAX_ITERATION = int(100000 + 1)
NUM_OF_CLASSESS = 11       # 레이블 개수
IMAGE_SIZE = 224

# VGGNet 그래프 구조를 구축합니다.
def vgg_net(weights, image):
  layers = (
    'conv1_1', 'relu1_1', 'conv1_2', 'relu1_2', 'pool1',

    'conv2_1', 'relu2_1', 'conv2_2', 'relu2_2', 'pool2',

    'conv3_1', 'relu3_1', 'conv3_2', 'relu3_2', 'conv3_3',
    'relu3_3', 'conv3_4', 'relu3_4', 'pool3',

    'conv4_1', 'relu4_1', 'conv4_2', 'relu4_2', 'conv4_3',
    'relu4_3', 'conv4_4', 'relu4_4', 'pool4',

    'conv5_1', 'relu5_1', 'conv5_2', 'relu5_2', 'conv5_3',
    'relu5_3', 'conv5_4', 'relu5_4'
  )

  net = {}
  current = image
  for i, name in enumerate(layers):
    kind = name[:4]
    # Convolution 레이어일 경우
    if kind == 'conv':
      kernels, bias = weights[i][0][0][0][0]
      # matconvnet: weights are [width, height, in_channels, out_channels]
      # tensorflow: weights are [height, width, in_channels, out_channels]
      # MATLAB 파일의 행렬 순서를 tensorflow 행렬의 순서로 변환합니다.
      #print('바꾸기 전 :' , kernels.shape)
      kernels = utils.get_variable(np.transpose(kernels, (1, 0, 2, 3)), name=name + "_w")
      #print('바꾼 후 :', kernels.shape)
      bias = utils.get_variable(bias.reshape(-1), name=name + "_b")
      current = utils.conv2d_basic(current, kernels, bias)

    # Activation 레이어일 경우
    elif kind == 'relu':
      current = tf.nn.relu(current, name=name)
    # Pooling 레이어일 경우
    elif kind == 'pool':
      current = utils.avg_pool_2x2(current)
    net[name] = current

  return net

# FCN 그래프 구조를 정의합니다.
def inference(image, keep_prob):
  """
  FCN 그래프 구조 정의
  arguments:
    image: 인풋 이미지 0-255 사이의 값을 가지고 있어야합니다.
    keep_prob: 드롭아웃에서 드롭하지 않을 노드의 비율
  """
  # 다운로드 받은 VGGNet을 불러옵니다.
  print("setting up vgg initialized conv layers ...")
  model_data = utils.get_model_data(FLAGS.model_dir, MODEL_URL)

  mean = model_data['normalization'][0][0][0]
  mean_pixel = np.mean(mean, axis=(0, 1))

  weights = np.squeeze(model_data['layers'])

  # 이미지에 Mean Normalization을 수행합니다.
  processed_image = utils.process_image(image, mean_pixel)

  with tf.variable_scope("inference"):
    image_net = vgg_net(weights, processed_image)

    test = image_net["conv1_1"]
    print(test.shape)   #(?, 224, 224, 64)

    # VGGNet의 conv5(conv5_3) 레이어를 불러옵니다.
    conv_final_layer = image_net["conv5_3"]
    print(conv_final_layer.shape)  # (?, 14, 14, 512)

    # pool5를 정의합니다.
    pool5 = utils.max_pool_2x2(conv_final_layer)

    # conv6을 정의합니다.
    W6 = utils.weight_variable([7, 7, 512, 4096], name="W6")
    b6 = utils.bias_variable([4096], name="b6")
    conv6 = utils.conv2d_basic(pool5, W6, b6)
    relu6 = tf.nn.relu(conv6, name="relu6")
    relu_dropout6 = tf.nn.dropout(relu6, keep_prob=keep_prob)

    # conv7을 정의합니다. (1x1 conv)
    W7 = utils.weight_variable([1, 1, 4096, 4096], name="W7")
    b7 = utils.bias_variable([4096], name="b7")
    conv7 = utils.conv2d_basic(relu_dropout6, W7, b7)
    relu7 = tf.nn.relu(conv7, name="relu7")
    relu_dropout7 = tf.nn.dropout(relu7, keep_prob=keep_prob)

    # conv8을 정의합니다. (1x1 conv)
    W8 = utils.weight_variable([1, 1, 4096, NUM_OF_CLASSESS], name="W8")
    b8 = utils.bias_variable([NUM_OF_CLASSESS], name="b8")
    conv8 = utils.conv2d_basic(relu_dropout7, W8, b8)

    # FCN-8s를 위한 Skip Layers Fusion을 설정합니다.
    # 이제 원본 이미지 크기로 Upsampling하기 위한 deconv 레이어를 정의합니다.
    deconv_shape1 = image_net["pool4"].get_shape()
    W_t1 = utils.weight_variable([4, 4, deconv_shape1[3].value, NUM_OF_CLASSESS], name="W_t1")
    b_t1 = utils.bias_variable([deconv_shape1[3].value], name="b_t1")
    # conv8의 이미지를 2배 확대합니다.
    conv_t1 = utils.conv2d_transpose_strided(conv8, W_t1, b_t1, output_shape=tf.shape(image_net["pool4"]))
    # 2x conv8과 pool4를 더해 fuse_1 이미지를 만듭니다.
    fuse_1 = tf.add(conv_t1, image_net["pool4"], name="fuse_1")

    deconv_shape2 = image_net["pool3"].get_shape()
    W_t2 = utils.weight_variable([4, 4, deconv_shape2[3].value, deconv_shape1[3].value], name="W_t2")
    b_t2 = utils.bias_variable([deconv_shape2[3].value], name="b_t2")
    # fuse_1 이미지를 2배 확대 합니다.
    conv_t2 = utils.conv2d_transpose_strided(fuse_1, W_t2, b_t2, output_shape=tf.shape(image_net["pool3"]))
    # 2x fuse_1과 pool3를 더해 fuse_2 이미지를 만듭니다.
    fuse_2 = tf.add(conv_t2, image_net["pool3"], name="fuse_2")

    shape = tf.shape(image)
    deconv_shape3 = tf.stack([shape[0], shape[1], shape[2], NUM_OF_CLASSESS])
    W_t3 = utils.weight_variable([16, 16, NUM_OF_CLASSESS, deconv_shape2[3].value], name="W_t3")
    b_t3 = utils.bias_variable([NUM_OF_CLASSESS], name="b_t3")
    # fuse_2 이미지를 8배 확대합니다.
    conv_t3 = utils.conv2d_transpose_strided(fuse_2, W_t3, b_t3, output_shape=deconv_shape3, stride=8)

    # 최종 prediction 결과를 결정하기 위해 마지막 activation들 중에서 argmax로 최대값을 가진 activation을 추출합니다.
    annotation_pred = tf.argmax(conv_t3, dimension=3, name="prediction")

  return tf.expand_dims(annotation_pred, dim=3), conv_t3


def main(argv=None):
  #pdb.set_trace()
  # 인풋 이미지와 타겟 이미지, 드롭아웃 확률을 받을 플레이스홀더를 정의합니다.
  keep_probability = tf.placeholder(tf.float32, name="keep_probabilty")
  image = tf.placeholder(tf.float32, shape=[None, IMAGE_SIZE, IMAGE_SIZE, 3], name="input_image")
  annotation = tf.placeholder(tf.int32, shape=[None, IMAGE_SIZE, IMAGE_SIZE, 1], name="annotation")

  # FCN 그래프를 선언하고 TensorBoard를 위한 summary들을 지정합니다.
  pred_annotation, logits = inference(image, keep_probability)
  tf.summary.image("input_image", image, max_outputs=2)
  tf.summary.image("ground_truth", tf.cast(annotation, tf.uint8), max_outputs=2)
  tf.summary.image("pred_annotation", tf.cast(pred_annotation, tf.uint8), max_outputs=2)

  # 손실함수를 선언하고 손실함수에 대한 summary를 지정합니다.
  loss = tf.reduce_mean((tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,labels=tf.squeeze(annotation, squeeze_dims=[3]), name="entropy")))
  tf.summary.scalar("entropy", loss)

  # 옵티마이저를 선언하고 파라미터를 한스텝 업데이트하는 train_step 연산을 정의합니다.
  optimizer = tf.train.AdamOptimizer(FLAGS.learning_rate)
  train_step = optimizer.minimize(loss)

  # TensorBoard를 위한 summary들을 하나로 merge합니다.
  print("Setting up summary op...")
  summary_op = tf.summary.merge_all()

  #pdb.set_trace()    # 디버깅
  # training 데이터와 validation 데이터의 개수를 불러옵니다.
  print("Setting up image reader...")
  train_records, valid_records = scene_parsing.read_dataset(FLAGS.data_dir)
  print(len(train_records))
  print(len(valid_records))

  # training 데이터와 validation 데이터를 불러옵니다.
  print("Setting up dataset reader")
  image_options = {'resize': True, 'resize_size': IMAGE_SIZE}
  if FLAGS.mode == 'train':
    train_dataset_reader = dataset.BatchDatset(train_records, image_options)
    #print('-----------------------------------------------------------', train_dataset_reader)
  validation_dataset_reader = dataset.BatchDatset(valid_records, image_options)

  # 세션을 엽니다.
  sess = tf.Session()

  # 학습된 파라미터를 저장하기 위한 tf.train.Saver()와
  # tensorboard summary들을 저장하기 위한 tf.summary.FileWriter를 선언합니다.
  print("Setting up Saver...")
  saver = tf.train.Saver()
  summary_writer = tf.summary.FileWriter(FLAGS.logs_dir, sess.graph)

  # 변수들을 초기화하고 저장된 ckpt 파일이 있으면 저장된 파라미터를 불러옵니다.
  sess.run(tf.global_variables_initializer())
  ckpt = tf.train.get_checkpoint_state(FLAGS.logs_dir)
  print(ckpt)
  print(type(ckpt))
  if ckpt and ckpt.model_checkpoint_path:
    saver.restore(sess, ckpt.model_checkpoint_path)
    print("Model restored...(모델 복원됨)")

  pdb.set_trace()  # 디버깅
  if FLAGS.mode == "train":
    for itr in range(MAX_ITERATION):
      # 학습 데이터를 불러오고 feed_dict에 데이터를 지정합니다
      train_images, train_annotations = train_dataset_reader.next_batch(FLAGS.batch_size)
      #print("train_annotations.shape :", train_annotations.shape)
      feed_dict = {image: train_images, annotation: train_annotations, keep_probability: 0.85}
      #print(feed_dict)

      # train_step을 실행해서 파라미터를 한 스텝 업데이트합니다.
      sess.run(train_step, feed_dict=feed_dict)

      # 10회 반복마다 training 데이터 손실 함수를 출력합니다.
      if itr % 10 == 0:
        train_loss, summary_str = sess.run([loss, summary_op], feed_dict=feed_dict)
        print("반복(Step): %d, Training 손실함수(Train_loss):%g" % (itr, train_loss))
        summary_writer.add_summary(summary_str, itr)

      # 500회 반복마다 validation 데이터 손실 함수를 출력하고 학습된 모델의 파라미터를 model.ckpt 파일로 저장합니다.
      if itr % 500 == 0:
        valid_images, valid_annotations = validation_dataset_reader.next_batch(FLAGS.batch_size)
        valid_loss = sess.run(loss, feed_dict={image: valid_images, annotation: valid_annotations,
                                               keep_probability: 1.0})
        print("%s ---> Validation 손실함수(Validation_loss): %g" % (datetime.datetime.now(), valid_loss))
        saver.save(sess, FLAGS.logs_dir + "model.ckpt", itr)

  elif FLAGS.mode == "visualize":
    # validation data로 prediction을 진행합니다.
    valid_images, valid_annotations = validation_dataset_reader.get_random_batch(FLAGS.batch_size)
    pred = sess.run(pred_annotation, feed_dict={image: valid_images, annotation: valid_annotations,
                                                keep_probability: 1.0})
    valid_annotations = np.squeeze(valid_annotations, axis=3)
    pred = np.squeeze(pred, axis=3)

    # Input Data, Ground Truth, Prediction Result를 저장합니다.
    for itr in range(FLAGS.batch_size):
      utils.save_image(valid_images[itr].astype(np.uint8), FLAGS.logs_dir, name="inp_" + str(5+itr))
      utils.save_image(valid_annotations[itr].astype(np.uint8), FLAGS.logs_dir, name="gt_" + str(5+itr))
      utils.save_image(pred[itr].astype(np.uint8), FLAGS.logs_dir, name="pred_" + str(5+itr))
      print("Saved image: %d" % itr)

  # 세션을 닫습니다.
  sess.close()

# main 함수를 실행합니다.
if __name__ == "__main__":
  tf.app.run()