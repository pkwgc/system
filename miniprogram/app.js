const config = require('./config.js')

App({
  globalData: {
    userInfo: null,
    gameId: null,
    playerId: null,
    wsUrl: config.wsUrl,
    apiUrl: config.apiUrl,
    systemInfo: null
  },
  onLaunch() {
    wx.getSystemInfo({
      success: res => {
        this.globalData.systemInfo = res
      }
    })
  }
})
