<?php
namespace app\model;

use think\Model;

class User extends Model
{
    // 设置数据表名
    protected $name = 'users';
    
    // 设置字段信息
    protected $schema = [
        'id'          => 'int',
        'user_id'     => 'string',
        'key'         => 'string',
        'balance'     => 'decimal',
        'role'        => 'string',
        'status'      => 'string',
        'create_time' => 'datetime',
        'update_time' => 'datetime',
    ];

    // 自动写入时间戳
    protected $autoWriteTimestamp = true;

    // 生成用户唯一key
    public static function generateKey(): string
    {
        return md5(uniqid(mt_rand(), true));
    }

    // 生成API Token
    public function generateToken(): string
    {
        $salt = env('TOKEN.TOKEN_SALT', '');
        $expire = time() + intval(env('TOKEN.TOKEN_EXPIRE', 7200));
        $hash = md5($this->user_id . $this->key . $salt . $expire);
        return $hash . '.' . $expire;
    }

    // 从Token中获取用户
    public static function getUserFromToken(string $token): ?User
    {
        if (empty($token)) {
            return null;
        }

        $parts = explode('.', $token);
        if (count($parts) !== 2) {
            return null;
        }

        [$hash, $expire] = $parts;
        
        if (time() > intval($expire)) {
            return null;
        }

        $salt = env('TOKEN.TOKEN_SALT', '');
        $users = self::select();
        
        foreach ($users as $user) {
            $calculatedHash = md5($user->user_id . $user->key . $salt . $expire);
            if ($calculatedHash === $hash) {
                return $user;
            }
        }
        
        return null;
    }

    // Check if user is admin
    public function isAdmin(): bool
    {
        return $this->role === 'admin';
    }
}
