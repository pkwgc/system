<?php
// +----------------------------------------------------------------------
// | 控制台配置
// +----------------------------------------------------------------------
return [
    // 指令定义
    'commands' => [
        'user:create' => 'app\command\CreateUser',
        'test:db' => 'app\command\TestDb',
    ],
];