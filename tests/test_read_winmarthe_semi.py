#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import gridmarthe as gm


def test_read_sem_from_winmarthe():
    sem_file = 'tests/data/thickness.sem'
    ds = gm.load_marthe_grid(sem_file)
    print('Test read sem from winmarthe success!')


if __name__ == '__main__':
    test_read_sem_from_winmarthe()