# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved. 
#   
# Licensed under the Apache License, Version 2.0 (the "License");   
# you may not use this file except in compliance with the License.  
# You may obtain a copy of the License at   
#   
#     http://www.apache.org/licenses/LICENSE-2.0    
#   
# Unless required by applicable law or agreed to in writing, software   
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
# See the License for the specific language governing permissions and   
# limitations under the License.
import os
import sys
parent = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(parent, '../')))

import cv2
import unittest
import yaml
import argparse

from ppcv.ops import KeypointOp
from ppcv.core.config import ConfigParser


class TestKeypoint(unittest.TestCase):
    def setUp(self):
        self.config = 'configs/unittest/test_keypoint.yml'
        self.input = 'demo/hrnet_demo.jpg'
        self.cfg_dict = dict(config=self.config, input=self.input)
        cfg = argparse.Namespace(**self.cfg_dict)
        config = ConfigParser(cfg)
        config.print_cfg()
        self.model_cfg, self.env_cfg = config.parse()

    def test_detection(self):
        img = cv2.imread(self.input)[:, :, ::-1]
        inputs = [{"input.image": [img, img, img]}, ]
        kpt_op = KeypointOp(self.model_cfg[0]["KeypointOp"], self.env_cfg)

        result = kpt_op(inputs)


if __name__ == '__main__':
    unittest.main()
