from __future__ import print_function
import configargparse


parser = configargparse.ArgParser(default_config_files=['my_config.cfg'], description='Initailize/Train/Infer a Unet or FPN using backbones based on segmentation_model [https://github.com/qubvel/segmentation_models].')

#arg = parser.add_argument
arg = parser.add

arg = parser.add_argument
train_arg = parser.add_argument

arg('-c', is_config_file=True, help='config file path', metavar="/path/to/configargparse file")

arg('--gpuPCIID', type=int, default=0, help="The PCI BUS ID of GPU to use for training.")

arg('--expandInputChannels', action='store_true', help="Should the Input/Source Images be expanded to 3. Helpful for single channel greyscale to 3 channels. You should always pass this argument.")

arg('--numberofTargetChannels', type=int, default=1, help="Number of target channels. Default 1.")

arg('--freezeEncoderBackbone', action='store_true', help="Should we freeze the encoder/backbone for the first two epochs of training. If you do not specify this flag then the encoder weights are NOT frozen.")

arg('--reloadExistingWeights', action='store_true', help="Should we load existing weights for training? This is a toggled value of freezeEncoderBackbone value. If you don\"t specify this flag then no weights will be loaded.")

arg('--oldWeightsFilename', help="Relative/Absolute path to model weights that should used to initializing the network. ONLY VALID if reloadExistingWeights is True.")

arg('--architectureType', help="Unet or FPN type architecture. Default: FPN", default="FPN")

arg('--backboneEncoderWeightsName', help="imagenet, imagenet11k, etc. See image_classifiers PyPI package. Default: imagenet", default="imagenet")

arg('--backboneName', help="Name of the backbone. Example, resent152, inceptionresnetv2, etc. See image_classifiers PyPI package. Default: inceptionresnetv2", default="inceptionresnetv2")

arg('--activationFunction', help="Activation function for the last layer. Eg. \"linear\", \"sigmoid\", \"softmax\", \"tanh\", etc. Default: \"sigmoid\"", default="sigmoid")

arg('--outputModelPrefix', default='IncResV2FPN', help="IncResV2FPN, ResNet152FPN, UIncResV2Net, UResNet152Net")

arg('--outputModelSuffix', default='input_normalizeandscaleUint8_target_mask_normalizeMax_bcedice')

arg('--trained_h5', default='trained.h5', help = "Location of the trained model weights")

arg('--trained_json', default='trained.json', help = "Location of the trained model architecture")

arg('--trainingBatchSize', type=int, default=16)

arg('--inferenceBatchSize', type=int, default=4)

arg('--numCSEpochs', type = int, default=2, help = "Set number of cold start epochs for training just the decoder with encoder weights frozen in the network (FPN/Unet).")

arg('--numFTEpochs', type = int, default=25, help = "Set number of fine-tuning epochs for training the entire network (FPN/Unet).")

arg('--loss_function', default='dice_coef_loss_bce', help="\'mean_squared_error\', \'mean_absolute_error\', \'binary_crossentropy\', \'dice_coef_loss_bce\'")

arg('--h5fname', default='/gpfs/gsfs10/users/HiTIF/data/dl_segmentation_input/sigal_2d_BABE/WellE07/mcf10a_biorep1_welle03_60x_bin2/gudlap/20190517_090840/mcf10a_biorep1_welle03_babe_60x2_Resize_Factors_1p00_2p00_0p33_0p67_1p33_input_gt_derived_outputs.h5', help='Relative/Absolute path to the .h5 file containing the augmented uint8 image patches and targets.')

## Typical h5 dataset(s) generated by the KNIME Workflow
## knime://knime-server/HiTIF/Reddy/DL_Segmentation_Paper/HiTIF_AugmentInputGT_H5
'''
Dataset Name =  DAPI_uint16touint8_normalizeandscale  Shape =  [10500, 256, 256]  Type =  uint8
Dataset Name =  alongboundary_bool  Shape =  [10500, 256, 256]  Type =  bool
Dataset Name =  bitmask_bool  Shape =  [10500, 256, 256]  Type =  bool
Dataset Name =  bitmask_erosion_bool  Shape =  [10500, 256, 256]  Type =  bool
Dataset Name =  bitmask_labeled_uint16  Shape =  [10500, 256, 256]  Type =  uint16
Dataset Name =  bkg_bool  Shape =  [10500, 256, 256]  Type =  bool
Dataset Name =  distancemapnormalized_float32  Shape =  [10500, 256, 256]  Type =  float32
Dataset Name =  gblurradius1_float32  Shape =  [10500, 256, 256]  Type =  float32
'''
arg('--srcDatasetName', default='DAPI_uint16touint8_normalizeandscale')

arg('--tarDatasetName', action='append', help="for multiple targets define them this way: --tarDatasetName bitmask_erosion_bool --tarDatasetName alongboundary_bool --tarDatasetName bkg_bool")

arg('--targetDontUseAbsoluteValue', action='store_false', help="If you don\'t specify this then the target image values will be taken as numpy.absolute. This is required for glurradius1_float32 because the GaussianBlur is is positive inside the nucleus and negative outside the nuclei.")

arg('--useTTAForTesting', action='store_true', help="If you don\'t specify this then test-time-augmentation (mostly 5 rotations) will NOT be used.")

arg('--testinputnumpyfname', default='/gpfs/gsfs10/users/HiTIF/progs/dl_segmentation/segmentation_models/Sigal_WellE03/input_augmentedintensity_rotations/20180823_075547/WellE03_chunkindex_011_DAPI_uint16touint8_normalizeandscale_dtypeuint8_patches.npy', help='A numpy file containing the greysacle testing images of dimensions N*H*W. H and W should be divisible by 32.')

arg('--testpredictnumpyfname', default='/gpfs/gsfs10/users/HiTIF/progs/dl_segmentation/segmentation_models/Sigal_WellE03/input_augmentedintensity_rotations/20180823_075547/WellE03_chunkindex_011_bitmask.npy', help='A numpy file location for saving the prediction of input greysacle testing images.')



args = parser.parse_args()
print(args)
print("----------")
print(parser.format_values())
