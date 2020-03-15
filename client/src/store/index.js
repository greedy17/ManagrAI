import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

Vue.use(Vuex)

const STORAGE_HASH = '{storage_hash}'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
}

const mutations = {
}

const actions = {
}

const plugins = [
  createPersistedState({
    key: STORAGE_KEY,
  }),
]

const getters = {}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins,
})
