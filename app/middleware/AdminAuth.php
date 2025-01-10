<?php
namespace app\middleware;

use think\Request;

class AdminAuth
{
    public function handle(Request $request, \Closure $next)
    {
        $user = $request->user;
        if (!$user || !$user->isAdmin()) {
            return json(['code' => 403, 'message' => 'No admin privileges']);
        }
        return $next($request);
    }
}
