import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import * as Cookies from 'js-cookie'
import User from '@/services/users/'
import Status from '@/services/statuses'
// import { apiClient, apiErrorHandler } from '@/services/api'
import { MeetingWorkflows, SObjectPicklist, SObjects } from '@/services/salesforce/models'
import { ObjectField, CRMObjects } from '@/services/crm'

Vue.use(Vuex)

const STORAGE_HASH = '128adjfn2n'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  stages: null,
  filters: [],
  meetings: [],
  showToolbarNav: false,
  pollingData: {
    items: {},
    lastCheck: null,
  },
  templates: null,
  pollingItems: [],
  pricebooks: null,
  allOpps: [],
  chatOpps: [],
  allContacts: [],
  allAccounts: [],
  allLeads: [],
  messages: [],
  currentView: null,
  currentOpp: null,
  allPicklistOptions: null,
  apiPicklistOptions: null,
  shouldUpdatePollingData: false,
  itemsFromPollToUpdate: new Set(),
  meetingData: {},
  customObject: {
    task: null,
    verboseName: null,
    checker: null,
  },
  recordTypes: [],
  chatTitle: 'All Open Opportunities'
}

const mutations = {
  UPDATE_STAGES: (state, payload) => {
    state.stages = payload
  },
  UPDATE_USER: (state, payload) => {
    state.user = payload
  },
  UPDATE_FILTERS: (state, payload) => {
    state.filters = payload
  },
  UPDATE_USERTOKEN: (state, payload) => {
    state.token = payload
  },
  UPDATE_RECORD_TYPES: (state, payload) => {
    state.recordTypes = payload
  },
  UPDATE_CHAT_TITLE: (state, payload) => {
    state.chatTitle = payload
  },
  // Log out the user by resetting the state to defaults
  LOGOUT_USER(state) {
    state.token = null
    state.user = null
    state.stages = []
  },
  SAVE_ALL_OPPS(state, allOpps) {
    state.allOpps = allOpps
  },
  SAVE_CHAT_OPPS(state, chatOpps) {
    state.chatOpps = chatOpps
  },
  SAVE_ALL_CONTACTS(state, allContacts) {
    state.allContacts = allContacts
  },
  SAVE_ALL_LEADS(state, allLeads) {
    state.allLeads = allLeads
  },
  SAVE_ALL_ACCOUNTS(state, allAccounts) {
    state.allAccounts = allAccounts
  },
  SAVE_MEETINGS(state, meetings) {
    state.meetings = meetings
  },
  SAVE_TEMPLATES(state, templates) {
    state.templates = templates
  },
  SAVE_PRICEBOOKS(state, pricebooks) {
    state.pricebooks = pricebooks
  },
  SAVE_ALL_PICKLISTS(state, allPicklistOptions) {
    state.allPicklistOptions = allPicklistOptions;
  },
  SAVE_API_PICKLISTS(state, apiPicklistOptions) {
    state.apiPicklistOptions = apiPicklistOptions;
  },
  UPDATE_CUSTOM_OBJECT: (state, payload) => {
    state.customObject = payload
  },
  UPDATE_MESSAGES: (state, payload) => {
    state.messages.push(payload)
  },
  SET_VIEW: (state, payload) => {
    state.currentView = payload
  },
  SET_OPP: (state, payload) => {
    state.currentOpp = payload
  },
  SET_MEETING_DATA: (state, { id, data, success, retry }) => {
    let newData = {}
    newData['success'] = success
    newData['retry'] = retry
    newData['data'] = data
    console.log('NEW DATA IS HERE', newData)
    state.meetingData[id] = newData

  },
  EDIT_MESSAGES: (state, {
    id,
    value,
    gtMsg,
    generated,
    generatedType,
    generatedId,
    note }) => {

    let newMsg
    newMsg = state.messages.filter((message) => message.id === id)
    if (generated) {
      newMsg[0]['generated'] = generated
      newMsg[0]['generatedType'] = generatedType
      newMsg[0]['generatedId'] = generatedId
      newMsg[0]['value'] = value
      newMsg[0]['gtMsg'] = gtMsg
    } else {
      newMsg[0]['value'] = value
    }
    for (let i = 0; i < state.messages.length; i++) {
      if (state.messages[i].id === id) {
        state.messages[i] = newMsg[0];
        break;
      }
    }
  },
  REMOVE_MESSAGE: (state, id) => {
    state.messages = state.messages.filter(message => message.id !== id);
  },
  MESSAGE_UPDATED: (state, payload) => {
    let updatedMsg = state.messages.filter(msg => msg.id === payload.id)
    updatedMsg[0].updated = true
    updatedMsg[0].data = payload.data
    updatedMsg[0].value = `Successfully updated ${updatedMsg[0].resource}!`

    let indexToUpdate = state.messages.findIndex(obj => obj.id === payload.id);

    if (indexToUpdate !== -1) {
      state.messages.splice(indexToUpdate, 1, updatedMsg[0]);
    }
  },
  CLEAR_MESSAGES: (state) => {
    state.messages = []
    state.chatTitle = 'All Open Opportunities'
  }

}

const actions = {
  async updateStages({ state, commit }) {
    if (!state.token) return null

    const res = await Status.api.list({})

    commit('UPDATE_STAGES', res.results ? res.results : null)
  },
  updateChatTitle({ commit }, title) {
    commit('UPDATE_CHAT_TITLE', title)
  },
  async loadTemplates({ commit }) {
    try {
      const res = await User.api.getTemplates()
      commit('SAVE_TEMPLATES', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadMeetings({ commit }) {
    try {
      const res = await MeetingWorkflows.api.getMeetingList()
      commit('SAVE_MEETINGS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  setCurrentView({ commit }, view) {
    commit('SET_VIEW', view)
  },
  setCurrentOpp({ commit }, opp) {
    commit('SET_OPP', opp)
  },
  editMessages({ commit }, {
    id,
    value,
    gtMsg,
    generated,
    generatedType,
    generatedId,
    note }) {
    commit('EDIT_MESSAGES', {

      id,
      value,
      gtMsg,
      generated,
      generatedType,
      generatedId,
      note
    })
  },
  setMeetingData({ commit }, { id, data, success, retry }) {
    commit('SET_MEETING_DATA', { id, data, success, retry })
  },
  removeMessage({ commit }, id) {
    commit('REMOVE_MESSAGE', id)
  },
  updateMessages({ commit }, message) {
    commit('UPDATE_MESSAGES', message)
  },
  messageUpdated({ commit }, { id, data }) {
    commit('MESSAGE_UPDATED', { id, data })
  },
  clearMessages({ commit }) {
    commit('CLEAR_MESSAGES',)
  },
  changeFilters({ commit }, filters) {
    commit('UPDATE_FILTERS', filters)
  },
  async loadMoreChatOpps({ state, commit }, { page = 1, text }) {
    let resourceName = ''
    if (state.user.crm === 'SALESFORCE') {
      resourceName = 'Opportunity'
    } else if (state.user.crm === 'HUBSPOT') {
      resourceName = 'Deal'
    }
    let oldResults = []
    if (page > 1) {
      oldResults = state.chatOpps.results
    }
    let res = await CRMObjects.api.getObjects(resourceName, page, true, [['CONTAINS', 'Name', text]])
    res.results = [...oldResults, ...res.results]
    commit('SAVE_CHAT_OPPS', res)
    return res
  },
  async loadChatOpps({ state, commit }, page = 1) {
    let resourceName = ''
    if (state.user.crm === 'SALESFORCE') {
      resourceName = 'Opportunity'
    } else if (state.user.crm === 'HUBSPOT') {
      resourceName = 'Deal'
    }
    let oldResults = []
    if (page > 1) {
      oldResults = state.chatOpps.results
    }
    let res
    if (!state.filters.length) {
      res = await CRMObjects.api.getObjects(resourceName, page)
    } else {
      res = await CRMObjects.api.getObjects(resourceName, page, true, state.filters)
    }
    res.results = [...oldResults, ...res.results]
    commit('SAVE_CHAT_OPPS', res)
    return res
  },
  async loadAllOpps({ state, commit }, filters = []) {
    try {
      let res
      if (state.user.crm === 'SALESFORCE') {
        if (!filters.length) {
          filters = [['NOT_EQUALS', 'StageName', 'Closed Won'], ['NOT_EQUALS', 'StageName', 'Closed Lost']]
        }
        res = await CRMObjects.api.getObjectsForWorkflows('Opportunity', true, filters)
      } else {
        if (!filters.length) {
          filters = [['NOT_EQUALS', 'dealstage', 'closedwon'], ['NOT_EQUALS', 'dealstage', 'closedlost']]
        }
        res = await CRMObjects.api.getObjectsForWorkflows('Deal', true, filters)
      }
      commit('SAVE_ALL_OPPS', res.results)
      return res.results
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllAccounts({ state, commit }, filters = []) {
    try {
      let res
      if (state.user.crm === 'SALESFORCE') {
        res = await CRMObjects.api.getObjectsForWorkflows('Account', true, filters)
      } else {
        res = await CRMObjects.api.getObjectsForWorkflows('Company', true, filters)
      }
      commit('SAVE_ALL_ACCOUNTS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllContacts({ commit }, filters = []) {
    try {
      const res = await CRMObjects.api.getObjectsForWorkflows('Contact', true, filters)
      commit('SAVE_ALL_CONTACTS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllLeads({ state, commit }, filters = []) {
    if (state.user.crm === 'SALESFORCE') {
      try {
        const res = await CRMObjects.api.getObjectsForWorkflows('Lead', true, filters)
        commit('SAVE_ALL_LEADS', res.results)
      } catch (e) {
        console.log(e)
      }
    }

  },
  async loadPricebooks({ commit }) {
    try {
      const res = await SObjects.api.getObjects('Pricebook2')
      commit('SAVE_PRICEBOOKS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllPicklists({ commit }) {
    let obj = {}

    try {
      const res = await SObjectPicklist.api.listPicklists({ pageSize: 1000 })
      for (let i = 0; i < res.length; i++) {
        if (res[i].fieldRef) {
          obj[res[i].fieldRef.id] = res[i].values
        }
      }
    } catch (e) {
      console.log(e)
    } finally {
      commit('SAVE_ALL_PICKLISTS', obj)
    }
  },
  async loadApiPicklists({ commit }) {
    let obj = {}

    try {
      const res = await SObjectPicklist.api.listPicklists({ pageSize: 1000 })
      for (let i = 0; i < res.length; i++) {
        if (res[i].fieldRef) {
          obj[res[i].fieldRef.apiName] = res[i].values
        }
      }
    } catch (e) {
      console.log(e)
    } finally {

      commit('SAVE_API_PICKLISTS', obj)
    }
  },
  async checkTask({ commit }, vbName) {
    try {
      const task = await User.api.checkTasks(vbName)
      commit('UPDATE_CUSTOM_OBJECT', { ...state.customObject, task })
    } catch (e) {
      console.log(e)
    }
  },
  async setCustomObject({ commit, dispatch }, name) {
    try {
      await SObjects.api.getCustomObjectFields(name).then((res) => {
        const vbName = res.verbose_name
        // state.customObject.checker = setInterval(() => {
        //   dispatch('checkTask', vbName)
        //   // this.loaderText = this.loaderTextList[this.changeLoaderText()]
        // }, 2000)
        commit('UPDATE_CUSTOM_OBJECT', { ...state.customObject, task: null })
      })
    } catch (e) {
      console.log(e)
    }
  },
  async getRecords({ commit }) {
    const res = await SObjects.api.getRecords()
    commit('UPDATE_RECORD_TYPES', res)
  },
  updateUser({ commit }, payload) {
    commit('UPDATE_USER', payload)
  },
  updateUserToken({ commit }, payload) {
    commit('UPDATE_USERTOKEN', payload)
  },
  async logoutUser({ state, commit }) {
    await User.api.logout()
    commit('LOGOUT_USER')
  },
  refreshCurrentUser({ state, commit }) {
    if (!state.token) {
      return null
    }
    return User.api
      .getUser(state.user.id)
      .then(user => {
        commit('UPDATE_USER', user)
        return user
      })
      .catch(() => {
        // do nothing for now
        return null
      })
  },
}

const plugins = [
  createPersistedState({
    key: STORAGE_KEY,
    // storage: window.sessionStorage
  }),
]

const getters = {
  userIsLoggedIn: state => {
    return !!(state.token && state.user)
  },
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins,
})
