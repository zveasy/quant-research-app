"""Simple GAN for generating log-returns."""

from __future__ import annotations

import numpy as np
from keras import layers, models, optimizers
from keras.callbacks import ModelCheckpoint


def build_generator(input_dim: int, cond_dim: int) -> models.Model:
    inp = layers.Input(shape=(input_dim + cond_dim,))
    x = layers.Dense(32)(inp)
    x = layers.LeakyReLU()(x)
    x = layers.Dense(32)(x)
    x = layers.LeakyReLU()(x)
    x = layers.Dense(32)(x)
    x = layers.LeakyReLU()(x)
    out = layers.Dense(input_dim)(x)
    return models.Model(inp, out, name="generator")


def build_discriminator(input_dim: int, cond_dim: int) -> models.Model:
    inp = layers.Input(shape=(input_dim + cond_dim,))
    x = layers.Dense(32)(inp)
    x = layers.LeakyReLU()(x)
    x = layers.Dense(32)(x)
    x = layers.LeakyReLU()(x)
    x = layers.Dense(32)(x)
    x = layers.LeakyReLU()(x)
    out = layers.Dense(1, activation="sigmoid")(x)
    return models.Model(inp, out, name="discriminator")


def train(data: np.ndarray, cond: np.ndarray, steps: int = 10000) -> None:
    input_dim = data.shape[1]
    cond_dim = cond.shape[1]
    gen = build_generator(input_dim, cond_dim)
    disc = build_discriminator(input_dim, cond_dim)

    opt = optimizers.Adam(0.0002)
    disc.compile(loss="binary_crossentropy", optimizer=opt)

    z_dim = input_dim
    checkpoint = ModelCheckpoint("gan_gen.h5", save_weights_only=True, period=1000)

    for step in range(steps):
        idx = np.random.randint(0, data.shape[0], 32)
        real_cond = cond[idx]
        real = data[idx]
        z = np.random.normal(size=(32, z_dim))
        fake = gen.predict(np.concatenate([z, real_cond], axis=1), verbose=0)
        X_real = np.concatenate([real, real_cond], axis=1)
        X_fake = np.concatenate([fake, real_cond], axis=1)
        y_real = np.ones((32, 1))
        y_fake = np.zeros((32, 1))
        disc.train_on_batch(X_real, y_real)
        disc.train_on_batch(X_fake, y_fake)
        z = np.random.normal(size=(32, z_dim))
        cond_batch = real_cond
        misleading = np.ones((32, 1))
        disc.trainable = False
        gen_in = np.concatenate([z, cond_batch], axis=1)
        combined = models.Model(gen.input, disc(models.layers.concatenate([gen.output, cond_batch], axis=1)))
        combined.compile(loss="binary_crossentropy", optimizer=opt)
        combined.train_on_batch(gen_in, misleading)
        disc.trainable = True
        if step % 1000 == 0:
            gen.save_weights(f"gan_gen_{step}.h5")
    gen.save_weights("gan_gen_final.h5")
