const app = getApp()

Page({
  data: {
    showJoinForm: false,
    gameIdInput: '',
    playerName: ''
  },

  createGame() {
    wx.request({
      url: `${app.globalData.apiUrl}/game/create`,
      method: 'POST',
      success: (res) => {
        app.globalData.gameId = res.data.game_id
        this.setData({ showJoinForm: true })
      }
    })
  },

  joinGame() {
    this.setData({ showJoinForm: true })
  },

  confirmJoin() {
    const gameId = this.data.gameIdInput || app.globalData.gameId

    wx.request({
      url: `${app.globalData.apiUrl}/game/${gameId}/join`,
      method: 'POST',
      data: {
        player_name: this.data.playerName
      },
      success: (res) => {
        app.globalData.playerId = res.data.player_id
        app.globalData.gameId = gameId

        wx.navigateTo({
          url: '/pages/game/game'
        })
      }
    })
  }
})
