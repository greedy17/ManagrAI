<template>
  <div class="alerts-page" :style="noRenderHeader ? 'margin-top: 0rem;' : ''">
    <div v-if="!noRenderHeader" class="alerts-header">
      <button @click="$router.push({ name: 'ListTemplates' })" class="back-button">
        <img src="@/assets/images/left.svg" height="14px" alt="" />
        Back
      </button>

      <h3>{{ config.title }}</h3>

      <div v-if="hasSlack">
        <PulseLoadingSpinnerButton
          :loading="savingTemplate"
          :class="!verifySubmit() || savingTemplate ? 'disabled__button' : 'purple__button'"
          text="Activate Template"
          @click.stop="onSave"
          :disabled="!verifySubmit() || savingTemplate"
        />
      </div>

      <div v-else>
        <button
          v-if="largeOpps"
          :disabled="!selectFieldBool || !largeOppsBool"
          @click="noSlackSave"
          :class="!selectFieldBool || !largeOppsBool ? 'disabled__button' : 'purple__button '"
        >
          Activate without Slack
        </button>
        <button
          v-else
          @click="noSlackSave"
          :disabled="selectField ? !selectFieldBool : null"
          :class="selectField && !selectFieldBool ? 'disabled__button' : 'purple__button '"
        >
          Activate without Slack
        </button>
      </div>
    </div>
    <div v-else class="alerts-header-inner">
      <button @click="closeBuilder" class="back-button">
        <img src="@/assets/images/left.svg" height="14px" alt="" />
        Back
      </button>

      <h3>{{ config.title }}</h3>

      <div v-if="hasSlack">
        <PulseLoadingSpinnerButton
          :loading="savingTemplate"
          :class="!verifySubmit() || savingTemplate ? 'disabled__button' : 'purple__button'"
          text="Activate Template"
          @click.stop="onSave"
          :disabled="!verifySubmit() || savingTemplate"
        />
      </div>

      <div v-else>
        <button
          v-if="largeOpps"
          :disabled="!selectFieldBool || !largeOppsBool"
          @click="noSlackSave"
          :class="!selectFieldBool || !largeOppsBool ? 'disabled__button' : 'purple__button '"
        >
          Activate without Slack
        </button>
        <button
          v-else
          @click="noSlackSave"
          :disabled="selectField ? !selectFieldBool : null"
          :class="selectField && !selectFieldBool ? 'disabled__button' : 'purple__button '"
        >
          Activate without Slack
        </button>
      </div>
    </div>
    <div class="centered">
      <div
        class="forecast__collection"
        :key="i"
        v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
      >
        <div v-if="selectField">
          <div
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
          >
            <div style="padding-left: 12px" class="section" v-if="largeOpps">
              <h4 class="section__header">Select your "Amount" Field</h4>

              <div>
                <div :key="i" v-for="(alertOperand, i) in alertGroup.field.alertOperands.groups">
                  <div :class="i > 0 ? 'visible' : ''">
                    <div>
                      <div>
                        <FormField>
                          <template v-slot:input>
                            <Multiselect
                              placeholder="Select Field"
                              v-model="largeOpp"
                              :options="objectFields.list"
                              openDirection="below"
                              style="width: 20vw"
                              selectLabel="Enter"
                              track-by="apiName"
                              label="referenceDisplayLabel"
                            >
                              <template slot="noResult">
                                <p class="multi-slot">No results. Try loading more</p>
                              </template>
                              <template slot="afterList">
                                <p class="multi-slot__more" @click="objectFieldNextPage">
                                  Load More
                                  <img src="@/assets/images/plusOne.svg" alt="" />
                                </p>
                              </template>
                              <template slot="placeholder">
                                <p class="slot-icon">
                                  <img src="@/assets/images/search.svg" alt="" />
                                  Select Field
                                </p>
                              </template>
                            </Multiselect>
                          </template>
                        </FormField>
                      </div>

                      <div>
                        <h4 class="section__header">"Amount" is greater than:</h4>
                        <template>
                          <div>
                            <FormField
                              :errors="alertOperand.field.operandValue.errors"
                              v-model="largeOppValue"
                              :inputType="getInputType(alertOperand.field._operandIdentifier.value)"
                              large
                              bordered
                              placeholder="Enter a value"
                            />
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else style="padding-left: 12px" class="section">
              <h4 class="section__header">Select Field</h4>
              <Multiselect
                placeholder="Select Field"
                v-model="identity"
                :options="objectFields.list"
                openDirection="below"
                style="width: 20vw; margin-top: 0.75rem"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="objectFieldNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Field
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>
        <div
          v-if="!selectField || isEmpty"
          class="section"
          :errors="form.field.recurrenceDay.errors"
        >
          <h4 class="section__head">Select Delivery Day</h4>

          <section class="section__body">
            <div class="row__">
              <label :class="config.newConfigs[0].recurrenceFrequency == 'WEEKLY' ? 'base' : ''"
                >Weekly</label
              >
              <ToggleCheckBox
                v-if="hasSlack"
                @input="
                  config.newConfigs[0].recurrenceFrequency == 'WEEKLY'
                    ? (config.newConfigs[0].recurrenceFrequency = 'MONTHLY')
                    : (config.newConfigs[0].recurrenceFrequency = 'WEEKLY')
                "
                :value="config.newConfigs[0].recurrenceFrequency !== 'WEEKLY'"
                offColor="#41b883"
                onColor="#41b883"
                style="margin-left: 8px; margin-right: 8px"
              />
              <label :class="config.newConfigs[0].recurrenceFrequency == 'MONTHLY' ? 'base' : ''"
                >Monthly</label
              >
            </div>

            <div v-if="config.newConfigs[0].recurrenceFrequency == 'WEEKLY'">
              <div class="week-row">
                <span v-for="(day, i) in weeklyOpts" :key="i">
                  <input
                    type="checkbox"
                    @input="setDay($event.target.value)"
                    :id="day.value"
                    :value="day.value"
                    :disabled="!hasSlack"
                  />
                  <!-- v-model="config.newConfigs[0].recurrenceDays" -->
                  <label
                    :for="day.value"
                    :class="
                      config.newConfigs[0].recurrenceDays.includes(day.value) ? 'active-option' : ''
                    "
                    >{{ day.key.charAt(0) }}</label
                  >
                </span>
              </div>
            </div>
            <!-- <div v-if="config.newConfigs[0].recurrenceFrequency == 'WEEKLY'">
              <FormField>
                <template v-slot:input>
                  <Multiselect
                    :disabled="!hasSlack"
                    placeholder="Select Day"
                    @input="setDay($event)"
                    v-model="selectedDays"
                    :options="weeklyOpts"
                    openDirection="below"
                    style="width: 20vw"
                    selectLabel="Enter"
                    track-by="value"
                    label="key"
                    :multiple="true"
                    :closeOnSelect="false"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ hasSlack ? 'Select Days' : 'Connect slack' }}
                      </p>
                    </template>
                  </Multiselect>
                </template>
              </FormField>
            </div> -->
            <FormField
              id="delivery"
              v-if="config.newConfigs[0].recurrenceFrequency == 'MONTHLY'"
              placeholder="Day of month"
              v-model="config.newConfigs[0].recurrenceDay"
              small
            />
          </section>
        </div>
        <div v-if="userLevel == 'MANAGER'" class="section">
          <h4 class="section__head">Select Pipelines</h4>

          <div class="section__body">
            <FormField :errors="form.field.alertTargets.errors">
              <template v-slot:input>
                <Multiselect
                  :disabled="!hasSlack"
                  placeholder="Select Users"
                  @input="mapIds"
                  v-model="selectedUsers"
                  :options="userTargetsOpts"
                  openDirection="below"
                  style="width: 20vw"
                  selectLabel="Enter"
                  track-by="id"
                  :custom-label="selectUsersCustomLabel"
                  :multiple="true"
                  :closeOnSelect="false"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      {{ hasSlack ? 'Select Users' : 'Connect slack' }}
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
        </div>

        <div v-if="hasSlack" class="section">
          <h4 class="section__head">Select Delivery Method</h4>

          <div class="section__body">
            <div v-if="!channelName" class="row__">
              <label :class="!create ? 'base' : ''">Select #channel</label>
              <ToggleCheckBox
                style="margin-left: 8px; margin-right: 8px"
                @input="changeCreate"
                :value="create"
                offColor="#41b883"
                onColor="#41b883"
              />
              <label :class="create ? 'base' : ''">Create #channel</label>
            </div>

            <label v-else for="channel"
              >Alert will send to
              <span>{{ channelName }}</span>
            </label>
            <div
              style="
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                justify-content: flex-start;
              "
              v-if="create"
            >
              <input
                v-model="channelName"
                class="search__input"
                type="text"
                name="channel"
                id="channel"
                placeholder="Name your channel"
                @input="logNewName(channelName)"
              />
              <div v-if="!channelCreated" style="margin-top: 1.25rem">
                <button
                  v-if="channelName"
                  @click="createChannel(channelName)"
                  class="purple__button bouncy"
                >
                  Create Channel
                </button>
                <button v-else class="disabled__button">Create Channel</button>
              </div>
            </div>
            <div style="margin-top: 0.5rem" v-else>
              <template>
                <Multiselect
                  v-if="!directToUsers"
                  placeholder="Select Channel"
                  v-model="selectedChannel"
                  @input="setRecipient"
                  :options="userChannelOpts.channels"
                  openDirection="below"
                  style="width: 20vw"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                  :loading="dropdownLoading"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template slot="afterList">
                    <p
                      v-if="userChannelOpts.nextCursor"
                      class="multi-slot__more"
                      @click="listUserChannels(userChannelOpts.nextCursor)"
                    >
                      Load More
                      <img src="@/assets/images/plusOne.svg" alt="" />
                    </p>
                    <p v-else></p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Channels
                    </p>
                  </template>
                </Multiselect>
              </template>
              <div v-if="userLevel !== 'REP'" class="sendAll custom-checkbox">
                <input type="checkbox" id="allUsers" v-model="directToUsers" />
                <label for="allUsers">Send directly to users</label>
              </div>

              <div v-else class="sendAll custom-checkbox">
                <input type="checkbox" id="allUsers" v-model="directToUsers" />
                <label for="allUsers">Send to primary channel</label>
              </div>
            </div>
          </div>
        </div>
        <div style="margin-bottom: 8px; display: flex" class="section">
          <div style="">
            <h4 class="section__head">Slack Message</h4>
            <section class="section__body">
              <p style="margin-bottom: 0">
                This is the message you'll recieve in slack with your workflow.
              </p>
            </section>
            <div style="display: flex; overflow-y: auto; height: 28.75vh">
              <div style="margin-bottom: 1rem">
                <div v-if="formattedSlackMessage.length">
                  <draggable
                    v-model="formattedSlackMessage"
                    group="fields"
                    @start="drag = true"
                    @end="dragEnd"
                    class="drag-section"
                  >
                    <div
                      v-for="(message, i) in formattedSlackMessage"
                      :key="i"
                      style="
                        margin: 0.5rem;
                        padding: 6px 12px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        width: 27.5vw;
                        border: 1px solid #eeeeee;
                        border-radius: 8px;
                        cursor: pointer;
                      "
                    >
                      <div style="justify-self: start">
                        <div style="font-weight: 900; font-size: 0.75rem; display: flex">
                          <img src="@/assets/images/drag.svg" alt="" />
                          <div style="margin-top: 0.25rem; margin-left: 0.5rem">
                            {{ message.title }}
                          </div>
                        </div>
                        <!-- <div style="font-size: .6rem;">{ {{message.val}} }</div> -->
                      </div>
                      <div @click="removeMessage(i, message)">
                        <img src="@/assets/images/remove.svg" style="height: 1.2rem" />
                      </div>
                    </div>
                  </draggable>
                </div>
                <div
                  v-else
                  style="
                    margin: 0.5rem;
                    padding: 6px 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    width: 27.5vw;
                    border: 1px solid #eeeeee;
                    border-radius: 8px;
                  "
                >
                  <div style="justify-self: start">
                    <div style="font-weight: 900; font-size: 0.75rem; margin-bottom: 0.1rem">
                      Please Select an Option from the List
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div style="margin-right: 8px; height: fit-content" class="start">
            <section style="max-width: 19vw;">
              <div class="search-bar">
                <img src="@/assets/images/search.svg" style="height: 18px" alt="" />
                <input
                  @input="searchFields"
                  type="search"
                  :placeholder="`Search Fields`"
                  v-model="filterText"
                />
              </div>

              <div class="field-section__fields">
                <div>
                  <p v-for="(field, i) in filteredFields" :key="field.id" style="margin: 4px 0">
                    <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
                    <label :for="i"></label>
                    {{ field.label == 'Price Book Entry ID' ? 'Products' : field.label }}
                  </p>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
      <div v-if="!hasSlack && !selectField" class="overlay">
        <p class="text">
          <!-- <img src="@/assets/images/slackLogo.png" height="10px" class="margin-right-s" alt="" /> -->
          <span class="link" @click="goToConnect"> Connect Slack</span>
          in order to recieve notifications.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import FormField from '@/components/forms/FormField'
import draggable from 'vuedraggable'

import AlertTemplate, { AlertTemplateForm } from '@/services/alerts/'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import { INPUT_TYPE_MAP } from '@/services/salesforce/models'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'PopularWorkflows',
  props: ['selectField', 'largeOpps', 'config', 'isEmpty', 'noRenderHeader', 'closeBuilder'],
  components: {
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
    draggable,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      objectFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: { forAlerts: true, filterable: true, page: 1 },
      }),
      slackMessage: [],
      formattedSlackMessage: [],
      fields: CollectionManager.create({
        ModelClass: ObjectField,
        filters: {
          crmObject: alert.resourceType,
          forAlerts: true,
        },
        pagination: { size: 1000 },
      }),
      filterText: '',
      addedFields: [],
      dropdownLoading: null,
      selectedUsers: [],
      // selectedDays: null,
      selectedChannel: null,
      userChannelOpts: new SlackListResponse(),
      create: false,
      channelCreated: false,
      savingTemplate: false,
      channelName: '',
      identity: '',
      largeOpp: null,
      largeOppValue: '',
      setDaysBool: false,
      largeOppsBool: false,
      selectFieldBool: false,
      selectUsersBool: false,
      directToUsers: true,
      alertTemplateForm: new AlertTemplateForm(),
      // fields: CollectionManager.create({ ModelClass: ObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      alertTargetOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
        { key: 'My Team', value: 'TEAM' },
        { key: 'Everyone', value: 'ALL' },
        { key: 'SDR', value: 'SDR' },
      ],
      weeklyOpts: [
        { key: 'Monday', value: '0' },
        { key: 'Tuesday', value: '1' },
        { key: 'Wednesday', value: '2' },
        { key: 'Thursday', value: '3' },
        { key: 'Friday', value: '4' },
        { key: 'Saturday', value: '5' },
        { key: 'Sunday', value: '6' },
      ],
    }
  },
  async created() {
    if (this.user.slackRef) {
      await this.listUserChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
    }
    this.objectFields.filters = {
      ...this.objectFields.filters,
      crmObject: this.selectedResourceType,
    }
    if (this.isEmpty) {
      this.objectFields.filters = {
        crmObject: this.selectedResourceType,
        search: '',
        updatable: true,
      }
    }
    await this.objectFields.refresh()
    this.fields.filters = {
      ...this.fields.filters,
    }
    if (this.isEmpty) {
      this.fields.filters = {
        crmObject: this.selectedResourceType,
        search: '',
        updatable: true,
      }
    }
    await this.fields.refresh()
    this.slackMessage = this.config.messageTemplate.body.split('\n\n')
    const slackFormat = []
    for (let i = 0; i < this.slackMessage.length; i++) {
      const titleAndVal = this.slackMessage[i].split('\n')
      const titleFormatted = titleAndVal[0].slice(8, titleAndVal[0].length - 10)
      const valFormatted = titleAndVal[1].slice(3, titleAndVal[1].length - 2)
      // valFormatted is needed for addedFieldNames, since it is more precise than just the title for filtering
      slackFormat.push({ title: titleFormatted, val: valFormatted })
    }
    this.formattedSlackMessage = slackFormat
  },
  watch: {
    selectedResourceType: {
      immediate: true,
      async handler(val, prev) {
        if (prev && val !== prev) {
          this.alertTemplateForm = this.alertTemplateForm.reset()
          this.selectedResourceType = val
        }
        if (this.selectedResourceType) {
          this.fields.filters.crmObject = this.selectedResourceType
          this.fields.filters.page = 1
          if (this.isEmpty) {
            this.fields.filters = {
              crmObject: this.selectedResourceType,
              search: '',
              updatable: true,
            }
          }
          await this.fields.refresh()
        }
      },
    },
    resourceType: {
      async handler(val) {
        this.objectFields.filters = {
          ...this.objectFields.filters,
          filterable: true,
          crmObject: val,
        }
        if (this.isEmpty) {
          this.objectFields.filters = {
            crmObject: val,
            search: '',
            updatable: true,
          }
        }
        this.objectFields.refresh()
      },
    },
    largeOpp: function () {
      if (this.largeOpp) {
        this.config.newGroups[0].newOperands[0].operandIdentifier = this.largeOpp.apiName
        this.config.newGroups[0].newOperands[0].dataType = this.largeOpp.dataType
        this.selectFieldBool = true
      } else {
        this.config.newGroups[0].newOperands[0].operandIdentifier = ''
        this.selectFieldBool = false
      }
    },
    identity: function () {
      if (this.identity) {
        this.config.newGroups[0].newOperands[0].operandIdentifier = this.identity.apiName
        this.selectFieldBool = true
      } else {
        this.config.newGroups[0].newOperands[0].operandIdentifier = ''
        this.selectFieldBool = false
      }
    },
    largeOppValue: function () {
      if (this.largeOppValue) {
        this.config.newGroups[0].newOperands[0].operandValue = this.largeOppValue
        this.largeOppsBool = true
      } else {
        this.config.newGroups[0].newOperands[0].operandValue = ''
        this.largeOppsBool = false
      }
    },
    directToUsers: 'setDefaultChannel',
  },
  methods: {
    checkForChannel() {
      !this.hasRecapChannel ? (this.directToUsers = false) : (this.directToUsers = true)
    },
    selectUsersCustomLabel(prop) {
      return prop.fullName.trim() ? prop.fullName : prop.email
    },
    repsPipeline() {
      if (this.userLevel !== 'MANAGER') {
        this.config.newConfigs[0].alertTargets = ['SELF']
        this.selectUsersBool = true
      }
    },
    goToConnect() {
      this.$router.push({ name: 'Integrations' })
    },
    test(log) {
      console.log('log', log)
    },
    dragEnd() {
      const slackMesArr = []
      const slackBindingsArr = []
      for (let i = 0; i < this.formattedSlackMessage.length; i++) {
        slackMesArr.push(
          '<strong>' +
            this.formattedSlackMessage[i].title +
            '</strong> \n { ' +
            this.formattedSlackMessage[i].val +
            ' }',
        )
        slackBindingsArr.push(` ${this.formattedSlackMessage[i].val} `)
      }
      this.slackMessage = slackMesArr
      this.config.messageTemplate.body = this.slackMessage.join('\n\n')
      this.config.messageTemplate.bindings = slackBindingsArr
      this.drag = false
    },
    bindText(val, title) {
      const addedStr = `<strong>${title}</strong> \n { ${val} }`
      this.slackMessage.push(addedStr)
      this.formattedSlackMessage.push({ title, val })
      this.config.messageTemplate.body = this.slackMessage.join('\n\n')
      this.config.messageTemplate.bindings.push(` ${val} `)
    },
    removeMessage(i, removedField) {
      this.slackMessage = this.slackMessage.filter((mes, j) => j !== i)
      this.formattedSlackMessage = this.formattedSlackMessage.filter((mes, j) => j !== i)
      this.config.messageTemplate.bindings = this.config.messageTemplate.bindings.filter(
        (mes, j) => j !== i,
      )
      this.config.messageTemplate.body = this.slackMessage.join('\n\n')
      this.addedFields = [...this.addedFields.filter((f) => f.id != removedField.id)]
    },
    onAddField(field) {
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
      this.bindText(`${this.selectedResourceType}.${field.apiName}`, `${field.label}`)
    },
    searchFields() {
      this.fields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: {
          crmObject: this.selectedResourceType,
          search: this.filterText,
        },
      })
      this.fields.refresh()
    },
    setDefaultChannel() {
      this.directToUsers
        ? (this.config.newConfigs[0].recipients = ['default'])
        : (this.config.newConfigs[0].recipients = null)
    },
    verifySubmit() {
      if (this.largeOpps) {
        return (
          this.config.newGroups[0].newOperands[0].operandIdentifier &&
          this.config.newGroups[0].newOperands[0].operandValue &&
          this.config.newConfigs[0].alertTargets.length &&
          this.selectUsersBool &&
          this.selectFieldBool &&
          this.largeOppsBool
        )
      } else {
        return (
          (this.config.newConfigs[0].recurrenceDays.length ||
            this.config.newGroups[0].newOperands[0].operandIdentifier) &&
          this.config.newConfigs[0].alertTargets.length &&
          this.selectUsersBool &&
          (this.setDaysBool || this.selectFieldBool) &&
          this.config.messageTemplate.body.length
        )
      }
    },
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
    },
    handleUpdate() {
      this.loading = true

      User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    changeCreate() {
      this.create = !this.create
    },
    async objectFieldNextPage() {
      await this.objectFields.addNextPage()
    },
    async listUserChannels(cursor = null) {
      this.dropdownLoading = true
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
      setTimeout(() => {
        this.dropdownLoading = false
      }, 500)
    },
    async createChannel(name) {
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = res.channel
        this.config.newConfigs[0].recipients = [res.channel.id]
        this.channelCreated = !this.channelCreated
      } else {
        this.channelName = ''
        if (res.error == 'name_taken') {
          this.$toast('Channel name already taken', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'invalid_name_maxlength') {
          this.$toast('Channel name exceeds max-length', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'restricted_action') {
          this.$toast('A team preference is preventing you from creating channels', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'invalid_name_specials') {
          this.$toast(
            'The only special characters allowed are hyphens and underscores. Channel names must also begin with a letter ',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'org_login_required') {
          this.$toast(
            'The workspace is undergoing an enterprise migration and will not be available until migration is complete.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'too_many_convos_for_team') {
          this.$toast('The workspace has exceeded its limit of public and private channels.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'no_permission') {
          this.$toast(
            'The workspace token used in this request does not have the permissions necessary to complete the request. Make sure your app is a member of the conversation its attempting to post a message to.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'team_access_not_granted') {
          this.$toast(
            'You are not granted the specific workspace access required to complete this request.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'invalid_name') {
          this.$toast('Channel name invalid. Please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Something went wrong, please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          console.log(res.error)
        }
      }
    },
    logNewName(str) {
      let new_str = ''
      new_str = str.replace(/\s+/g, '-').toLowerCase()
      this.channelName = new_str
    },
    setRecipient() {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value =
        this.selectedChannel
      this.config.newConfigs[0].recipients = [this.selectedChannel.id]
    },
    setDay(n) {
      const recurrenceDays = this.config.newConfigs[0].recurrenceDays
      let index
      for (let i = 0; i < recurrenceDays.length; i++) {
        const day = recurrenceDays[i]
        if (day === n) {
          index = i
          break
        }
      }
      if (index !== undefined) {
        // if it exists in the array, remove
        this.config.newConfigs[0].recurrenceDays = recurrenceDays.filter((day, i) => i !== index)
      } else {
        // if it doesn't exist, add
        this.config.newConfigs[0].recurrenceDays.push(n)
      }
      this.setDaysBool = !!this.config.newConfigs[0].recurrenceDays.length
    },
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)
      this.config.newConfigs[0].alertTargets = mappedIds
      this.selectUsersBool = true
    },
    async noSlackSave() {
      this.savingTemplate = true
      try {
        const res = await AlertTemplate.api.createAlertTemplate({
          ...this.config,
          user: this.$store.state.user.id,
          directToUsers: true,
        })

        this.handleUpdate()

        this.$toast('Workflow saved successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.$router.push({ name: 'CreateNew' })
      } catch (e) {
        this.$toast('One or more of your users do not have slack connected', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.savingTemplate = false
      }
    },
    async onSave() {
      this.savingTemplate = true
      const newConfigs = this.config.newConfigs[0]
      const operandIden = this.config.newGroups[0].newOperands[0].operandIdentifier
      let largeOpsCheck = true
      if (this.largeOpps) {
        largeOpsCheck = false
        if (this.largeOppsBool) {
          largeOpsCheck = true
        }
      }
      if (
        (newConfigs.recurrenceDays.length || operandIden) &&
        newConfigs.alertTargets.length &&
        this.selectUsersBool &&
        largeOpsCheck &&
        (this.setDaysBool || this.selectFieldBool)
      ) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate({
            ...this.config,
            user: this.$store.state.user.id,
            directToUsers: this.directToUsers,
          })

          if (res.status === 400 && res.data.message) {
            this.$toast(res.data.message, {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            return
          }

          this.handleUpdate()

          this.$toast('Workflow saved Successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.$router.push({ name: 'ListTemplates' })
        } catch (e) {
          console.log('e', e)
          this.$toast(`${e}`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.savingTemplate = false
        }
      }
    },
  },

  computed: {
    hasRecapChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.recapChannel
        : null
    },
    filteredFields() {
      return this.fields.list.filter(
        (field) => !this.addedFieldNames.includes(`${this.selectedResourceType}.${field.apiName}`),
      )
    },
    addedFieldNames() {
      return this.formattedSlackMessage.map((field) => {
        return field.val.trim()
      })
    },
    userLevel() {
      return this.$store.state.user.userLevel
    },
    userTargetsOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertTargetOpts.map((opt) => {
            return {
              id: opt.value,
              fullName: opt.key,
            }
          }),
          ...this.users.list,
        ]
      } else {
        return [{ fullName: 'Myself', id: 'SELF' }]
      }
    },
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
    user() {
      return this.$store.state.user
    },
    selectedResourceType: {
      get() {
        return this.config.resourceType
      },
      set(val) {
        this.config.resourceType = val
      },
    },
  },
  mounted() {
    this.repsPipeline()
    this.checkForChannel()
    this.setDefaultChannel()
  },
  beforeMount() {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';

::v-deep .input-content {
  width: 20vw;
  border: 1px solid #e8e8e8 !important;
  border-radius: 0.3rem;
  background-color: white;
  box-shadow: none !important;
}
::v-deep .input-form {
  width: 20vw;
}
::v-deep .input-form__active {
  border: none;
}
.active-option {
  color: $base-gray !important;
  border: 1px solid $base-gray !important;
}
.week-row {
  display: flex;
  flex-direction: row;
  align-items: center !important;
  width: 25vw;
  overflow-x: scroll;
  margin-top: 16px;

  span {
    transition: all 0.2s;
  }
  label {
    cursor: pointer;
    color: $light-gray-blue;
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 26px;
    width: 26px;
    border-radius: 100%;
    border: 1px solid $soft-gray;
    transition: all 0.2s;
  }
  input {
    display: none;
  }
  span:hover {
    transform: scale(1.15);
    color: $base-gray;
  }

  // span {
  //   cursor: pointer;
  //   color: $light-gray-blue;
  //   margin-right: 8px;
  //   display: flex;
  //   align-items: center;
  //   justify-content: center;
  //   height: 26px;
  //   width: 26px;
  //   border-radius: 100%;
  //   border: 1px solid $soft-gray;
  //   transition: all 0.2s;
  //   input {
  //     display: none;
  //   }
  // }

  // span:hover {
  //   transform: scale(1.15);
  //   color: $base-gray;
  // }
}
.centered {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 16px;
}
.custom-checkbox > input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 1.3ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}
.custom-checkbox > input[type='checkbox'] {
  line-height: 2.1ex;
}
.custom-checkbox > input[type='checkbox'] {
  position: absolute;
  left: -999em;
}
.custom-checkbox > input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
.custom-checkbox > input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
.sendAll {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  font-size: 12px;
  color: $base-gray;
  margin-top: 1rem;
}
@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.section {
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  border: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  width: 50vw;
  min-height: 25vh;
  letter-spacing: 0.75px;
  padding: 0px 0px 32px 0px;
  margin-top: 16px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    // color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    color: $light-gray-blue;
    p {
      margin-top: 0;
    }
  }
}
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 60px;
  background-color: $white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $light-gray-blue;
  }
}
.alerts-header-inner {
  // position: fixed;
  z-index: 10;
  // top: 0;
  // left: 60px;
  background-color: $white;
  // width: 96vw;
  position: sticky;
  top: 0;
  width: 100%;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    color: $light-gray-blue;
  }
}
.back-button {
  color: $base-gray;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  font-size: 16px;
  letter-spacing: 0.75px;

  img {
    margin-right: 8px;
  }
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}

::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
.search__input {
  font-family: Lato-Regular, sans-serif;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  font-size: 16px;
  border-radius: 4px;
  line-height: 1.29;
  letter-spacing: 0.5px;
  height: 2.5rem;
  background-color: white;
  border: 1px solid $soft-gray;
  margin-top: 1rem;
  width: 20vw;
}
input[type='text']:focus {
  outline: none;
}
.purple__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  min-width: 10rem;
  font-size: 14px;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $gray;
  cursor: not-allowed;

  font-size: 14px;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  letter-spacing: 0.75px;
  margin-bottom: 8px;
}
input {
  cursor: pointer;
}
.visible {
  visibility: hidden;
}
.forecast__collection {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}
img {
  filter: invert(40%);
}
.alerts-page {
  height: 100vh;
  color: $base-gray;
  margin-top: 11vh;
}
.base {
  color: $base-gray;
}
.overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  // left: 0;
  // right: 0;
  height: 100%;
  width: 80%;
  padding-left: 10vw;
  padding-right: 10vw;
  opacity: 0;
  transition: 0.5s ease;
  background-color: $dark-green;
  border-radius: 5px;
}
.container:hover .overlay {
  opacity: 0.85;
}
.text {
  color: white;
  font-size: 16px;
  position: absolute;
  top: 50%;
  left: 50%;
  -webkit-transform: translate(-50%, -50%);
  -ms-transform: translate(-50%, -50%);
  transform: translate(-50%, -50%);
  text-align: center;
}
// .margin-right-s {
//   margin-right: 0.5rem;
// }
.link {
  border-bottom: 1px solid white;
  cursor: pointer;
}
.search-bar {
  background-color: white;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 8px;
  margin-top: 16px;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 15vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
.field-section {
  width: 20vw;
  background-color: white;
  height: 100%;
  margin-top: 28px;
  margin-left: 16px;
  padding: 0px 32px;
  border-radius: 6px;
  letter-spacing: 0.75px;

  &__title {
    letter-spacing: 0.75px;
  }
  &__fields {
    h4 {
      font-size: 13px;
      font-weight: 400;
      margin-bottom: 8px;
    }
    p {
      font-size: 12px;
      letter-spacing: 0.75px;
    }
    div {
      outline: 1px solid $soft-gray;
      border-radius: 6px;
      padding: 4px 16px;
      margin-top: 16px;
      height: 32vh;
      overflow: scroll;
      section {
        span {
          color: $coral;
          margin-left: 4px;
        }
      }
    }
  }
}
.inner-header {
  display: flex;
  justify-content: space-between;
}
::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}
::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}
</style>
