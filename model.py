
from utils import *
import numpy as np

# AMI-NET++ with only binary features
class Graph(tf.keras.Model):

    def __init__(self, tokens, d_model, feat_max, num_heads, rate):

        super(Graph, self).__init__()

        self.embedding = tf.keras.layers.Embedding(tokens, d_model)
        self.multihead_att = MultiHeadAttention(d_model, num_heads)
        self.pooling = MIL_gated_attention(feat_max)
        self.ln = tf.keras.layers.LayerNormalization(epsilon=1e-6)

        self.w1 = tf.keras.layers.Dense(d_model/2, activation='relu')
        self.w2 = tf.keras.layers.Dense(d_model/4)

        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)


    def call(self, x_bin):

        # word embedding
        x = self.embedding(x_bin)

        # multi-head attention
        mha_out, mha_att_matrix = self.multihead_att(x, x, x)
        mha_out = self.dropout1(mha_out)
        out = self.ln(x + mha_out)

        # fully connected layers
        x_dense1 = self.w1(out)
        x_dense2 = self.w2(x_dense1)
        x_dense2_drop = self.dropout2(x_dense2)

        # Instance-level Pooling
        rep = tf.reduce_sum(x_dense2_drop, axis=-1)

        # Bag-level Pooling
        mil_out, mil_att_matrix = self.pooling(rep)
        pred = tf.nn.sigmoid(mil_out)

        return pred, mha_att_matrix, mil_att_matrix
