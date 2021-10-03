<template>
  <div class="alerts-page">
    <Modal ref="templateModal">
      <template v-slot:header>
        <h3>Message Templates</h3>
      </template>
      <template v-slot:body>
        <div class="template__border">
          <h3 style="color: #199e54">Close Date Passed</h3>
          <p>
            Hey <strong style="color: #beb5cc">{ __Recipient.full_name }</strong> , your deal
            <strong style="color: #beb5cc">{ Opportunity.Name }</strong> has a passed closed date.
            Please update it!
          </p>
        </div>

        <div class="template__border">
          <h3 style="color: #199e54">New Opportunity</h3>
          <p>
            2. <strong style="color: #beb5cc">{ Opportunity.Name }</strong> is a new Opp booked for
            this week! The appointment was booked via
            <strong style="color: #beb5cc">{ Opportunity.LeadSource }</strong>
            !
          </p>
          <p>
            Handoff notes: <strong style="color: #beb5cc">{ Opportunity.Handoff_Notes_c }</strong>
          </p>
          <p style="margin-top: -0.75rem">
            Using a Competitor:
            <strong style="color: #beb5cc">{ Opportunity.Competitors_c }</strong>
          </p>
          <p style="margin-top: -0.75rem">
            Meeting date:
            <strong style="color: #beb5cc">{ Opportunity.Meeting_Date_c }</strong>
          </p>
        </div>

        <div class="template__border">
          <h3 style="color: #199e54">Update Forecast</h3>
          <p>
            3. Please update the forecast for
            <strong style="color: #beb5cc">{ Opportunity.Name }</strong>
            ! it's expected to close on
            <strong style="color: #beb5cc">{ Opportunity.CloseDate }</strong> and forecasted as
            <strong style="color: #beb5cc">{ Opportunity.ForecastCategoryName }</strong> - please
            either move to Commit or update the Close Date.
          </p>
          <p>Next Step: <strong style="color: #beb5cc">{ Opportunity.NextStep }</strong></p>
        </div>
      </template>
    </Modal>

    <div v-if="pageNumber === 0">
      <h3 style="text-align: center; color: black" class="title">
        {{ alertTemplateForm.field.resourceType.value }} Selected. Switch to
        <span
          v-if="selectedResourceType === 'Opportunity'"
          v-on:click="accountResource"
          style="border-bottom: 3px solid #5d5e5e; cursor: pointer"
          >Account</span
        >
        <span
          v-else
          v-on:click="opportunityResource"
          style="border-bottom: 3px solid #5d5e5e; cursor: pointer"
          >Opporunity</span
        >
        or
        <span v-on:click="leadResource" style="border-bottom: 3px solid #5d5e5e; cursor: pointer"
          >Lead</span
        >
      </h3>
      <!-- <progress id="progress" value="0" max="5" ref="progress" style="margin-bottom: 2rem">
        1/5
      </progress> -->
    </div>

    <div class="alert__row">
      <div v-if="pageNumber === 0" class="alert__column__">
        <!-- <div class="alert_title" style="text-align: center">1. Select fields and operators</div> -->
        <div :key="index" v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups">
          <div class="sf__collection">
            <!-- <FormField
              id="alert-title"
              v-model="alertTemplateForm.field.title.value"
              placeholder="Name your alert (required)"
              :errors="alertTemplateForm.field.title.errors"
              @blur="alertTemplateForm.field.title.validate()"
            /> -->
            <AlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />
            <div class="fixed__right" v-if="alertTemplateForm.field.alertGroups.groups.length > 1">
              <button class="remove__group" @click="onRemoveAlertGroup(index)">
                <img
                  src="@/assets/images/trash.png"
                  style="height: 1.25rem; margin-left: 0.25rem"
                  alt=""
                />
              </button>
            </div>
          </div>
        </div>
        <div style="margin-top: 0.5rem">
          <button class="plus_button" @click="onAddAlertGroup">
            <img src="@/assets/images/add.svg" class="filtered" alt="" />
          </button>
        </div>
      </div>

      <div v-if="pageNumber === 2" class="alert__column">
        <div class="alert_title" style="text-align: center">3. Construct your Message</div>
        <div class="collection__fields">
          <div class="message_titles">
            <h3>Customize your Slack Message</h3>
            <p style="margin-top: -1rem">
              Copy and paste the
              <span
                @click="$refs.templateModal.openModal()"
                style="color: #199e54; cursor: pointer; border-bottom: 2px solid #199e54"
                >template.</span
              >
            </p>
            <FormField
              id="message"
              :errors="alertTemplateForm.field.alertMessages.groups[0].field.body.errors"
            >
              <template v-slot:input>
                <quill-editor
                  @blur="alertTemplateForm.field.alertMessages.groups[0].field.body.validate()"
                  ref="message-body"
                  v-model="alertTemplateForm.field.alertMessages.groups[0].field.body.value"
                  :options="{
                    modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                    placeholder: 'Your alert message...',
                    theme: 'snow',
                  }"
                  class="message__box"
                />
              </template>
            </FormField>
          </div>

          <div class="message_titles">
            <h3>Add CRM Fields</h3>
            <DropDownSearch
              :items="fields.list"
              @input="bindText(`${selectedResourceType}.${$event}`)"
              displayKey="referenceDisplayLabel"
              valueKey="apiName"
              nullDisplay="Search"
              searchable
              :hasNext="!!fields.pagination.hasNextPage"
              @load-more="fieldNextPage"
              @search-term="onSearchFields"
              auto
            />
          </div>
        </div>
      </div>

      <div v-if="pageNumber === 1" class="alert__column">
        <!-- <div class="alert_title" style="text-align: center">2. Select Delivery Options</div> -->
        <div class="collection__">
          <template>
            <div
              class="delivery__row"
              :key="i"
              v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
            >
              <div
                style="
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: center;
                  border-right: 2px solid white;
                  padding: 1.5rem;
                "
              >
                <div class="row__">
                  <label>Weekly</label>
                  <ToggleCheckBox
                    style="margin: 0.25rem"
                    @input="
                      form.field.recurrenceFrequency.value == 'WEEKLY'
                        ? (form.field.recurrenceFrequency.value = 'MONTHLY')
                        : (form.field.recurrenceFrequency.value = 'WEEKLY')
                    "
                    :value="form.field.recurrenceFrequency.value !== 'WEEKLY'"
                    offColor="#199e54"
                    onColor="#199e54"
                  />
                  <label>Monthly</label>
                </div>

                <div>
                  <!-- <p style="color: #beb5cc">What day would you like your Smart Alert delivered:</p> -->

                  <div v-if="form.field.recurrenceFrequency.value == 'WEEKLY'">
                    <FormField>
                      <template v-slot:input>
                        <DropDownSearch
                          :items.sync="weeklyOpts"
                          :itemsRef.sync="form.field._recurrenceDay.value"
                          v-model="form.field.recurrenceDay.value"
                          displayKey="key"
                          valueKey="value"
                          nullDisplay="Select Day"
                          searchable
                          local
                        />
                      </template>
                    </FormField>
                    <!-- <div :key="value" v-for="(key, value) in weeklyOpts">
                      <span class="delivery__row">
                        <input
                          type="radio"
                          :value="key.value"
                          id="value"
                          v-model="form.field.recurrenceDay.value"
                          style="height: 1rem"
                          @click="setDay(key)"
                        />
                        <label style="margin-left: -3rem; margin-top: 0.5rem" for="value">{{
                          key.key
                        }}</label>
                      </span>
                    </div> -->
                  </div>

                  <FormField
                    style="margin-left: 1rem"
                    id="delivery"
                    v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
                    placeholder="Day of month"
                    @blur="form.field.recurrenceDay.validate()"
                    v-model="form.field.recurrenceDay.value"
                    small
                  />
                </div>
              </div>

              <div
                style="
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: space-evenly;
                  border-right: 2px solid white;
                  padding: 1.5rem;
                "
              >
                <span style="font-weight: bold">Whose pipelines?</span>
                <!-- <input
                  class="search__input"
                  type="text"
                  v-model="searchQuery"
                  placeholder="Search pipelines..."
                />

                <div :key="value" v-for="(key, value) in filteredUserTargets">
                  <span id="utops" class="delivery__row">
                    <input
                      v-model="form.field.alertTargets.value"
                      :value="key.id"
                      id="value"
                      type="checkbox"
                      style="height: 1rem"
                      @click="setPipelines(key)"
                    />
                    <label style="margin-left: -3rem; margin-top: 0.5rem" for="value">{{
                      key.fullName
                    }}</label>
                  </span>
                </div> -->
                <FormField :errors="form.field.alertTargets.errors">
                  <template v-slot:input>
                    <DropDownSearch
                      :items.sync="userTargetsOpts"
                      :itemsRef.sync="form.field._alertTargets.value"
                      v-model="form.field.alertTargets.value"
                      displayKey="fullName"
                      valueKey="id"
                      nullDisplay="Pipelines"
                      searchable
                      local
                    />
                  </template>
                </FormField>
              </div>

              <div
                style="
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: center;
                "
              >
                <div
                  class="row__"
                  style="display: flex; align-items: center; justify-content: center"
                >
                  <label>DM users</label>
                  <ToggleCheckBox
                    style="margin: 0.25rem"
                    @input="
                      form.field.recipientType.value == 'USER_LEVEL'
                        ? (form.field.recipientType.value = recipientTypeToggle(
                            form.field.recipientType.value,
                          ))
                        : (form.field.recipientType.value = recipientTypeToggle('SLACK_CHANNEL'))
                    "
                    :value="form.field.recipientType.value !== 'USER_LEVEL'"
                    offColor="#199e54"
                    onColor="#199e54"
                  />
                  <label>Send to #Channel</label>
                </div>

                <div v-if="form.field.recipientType.value == 'USER_LEVEL'">
                  <!-- <input
                    class="search__input"
                    type="text"
                    v-model="searchText"
                    placeholder="Search Recipients..."
                  />
                  <div :errors="form.field.recipients.errors" style="margin-bottom: 1rem">
                    <div :key="value" v-for="(key, value) in filteredRecipients">
                      <span class="delivery__row">
                        <input
                          v-model="form.field.recipients.value"
                          :value="key.id"
                          id="value"
                          type="checkbox"
                          style="height: 1rem"
                          @click="setRecipients(key)"
                        />
                        <label style="margin-left: -3rem; margin-top: 0.5rem" for="value">{{
                          key.fullName
                        }}</label>
                      </span>
                    </div>
                  </div> -->

                  <FormField :errors="form.field.recipients.errors">
                    <template v-slot:input>
                      <DropDownSearch
                        :items.sync="recipientOpts"
                        :itemsRef.sync="form.field._recipients.value"
                        v-model="form.field.recipients.value"
                        displayKey="fullName"
                        valueKey="id"
                        nullDisplay="Recipients"
                        searchable
                        local
                      />
                    </template>
                  </FormField>
                </div>
                <div v-if="form.field.recipientType.value == 'SLACK_CHANNEL'">
                  <!-- <input
                    class="search__input"
                    type="text"
                    v-model="searchChannels"
                    placeholder="Search Channels..."
                  />
                  <div class="channels_height">
                    <div :key="value" v-for="(key, value) in filteredChannels">
                      <input
                        @click="setRecipient(key)"
                        v-model="form.field.recipients.value"
                        :value="key.id"
                        type="radio"
                        id="value"
                        style="height: 1rem; margin-top: 0.5rem"
                      />
                      <label style="margin-left: -3rem; margin-bottom: 1rem" for="value">{{
                        key.name
                      }}</label>
                    </div>
                  </div> -->

                  <FormField :errors="form.field.recipients.errors">
                    <template v-slot:input>
                      <DropDownSearch
                        :items.sync="reversedChannels"
                        :itemsRef.sync="form.field._recipients.value"
                        v-model="form.field.recipients.value"
                        @input="form.field.recipients.validate()"
                        displayKey="name"
                        valueKey="id"
                        nullDisplay="Channels"
                        :hasNext="!!channelOpts.nextCursor"
                        @load-more="listChannels(channelOpts.nextCursor)"
                        searchable
                        local
                      >
                        <template v-slot:tn-dropdown-option="{ option }">
                          <!-- <img
                            v-if="option.isPrivate == true"
                            class="card-img"
                            src="@/assets/images/lockAsset.png"
                          /> -->
                          {{ option['name'] }}
                        </template>
                      </DropDownSearch>
                    </template>
                  </FormField>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div class="alert__column" v-if="pageNumber === 3">
        <div class="alert_title" style="text-align: center">4. Review and Save Smart Alert</div>

        <template>
          <div class="collection">
            <div style="display: flex; justify-content: center"></div>
            <AlertSummary :form="alertTemplateForm" />
          </div>
        </template>
      </div>
    </div>
    <div class="bottom_locked">
      <button
        @click="onPreviousPage"
        :class="pageNumber === 0 ? 'disabled__button' : 'gold__button'"
        style="margin-right: 0.5rem"
      >
        Prev
      </button>
      <button
        v-if="pageNumber < 3"
        @click="onNextPage"
        :class="pageNumber === 3 ? 'disabled__button' : 'purple__button'"
        style="margin-right: 2rem"
      >
        Next
      </button>
      <PulseLoadingSpinnerButton
        v-else
        :loading="savingTemplate"
        :class="
          !alertTemplateForm.isValid || savingTemplate ? 'disabled__button' : 'purple__button'
        "
        text="Save alert"
        @click.stop="onSave"
        :disabled="!alertTemplateForm.isValid || savingTemplate"
      />
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

import { quillEditor } from 'vue-quill-editor'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
//Internal
import FormField from '@/components/forms/FormField'
import AlertGroup from '@/views/settings/alerts/create/_AlertGroup'
import AlertSummary from '@/views/settings/alerts/create/_AlertSummary'
import ListContainer from '@/components/ListContainer'
import ListItem from '@/components/ListItem'
import SlackNotificationTemplate from '@/views/settings/alerts/create/SlackNotificationTemplate'
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import DropDownSearch from '@/components/DropDownSearch'
import ExpandablePanel from '@/components/ExpandablePanel'
import Modal from '@/components/Modal'

/**
 * Services
 */

import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CollectionSearch from '@thinknimble/collection-search'
import {
  SObjectField,
  SObjectValidations,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
} from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'AlertsPage',
  components: {
    ExpandablePanel,
    DropDownSearch,
    ListContainer,
    ListItem,
    SlackMessagePreview,
    AlertGroup,
    SlackNotificationTemplate,
    quillEditor,
    ToggleCheckBox,
    FormField,
    AlertSummary,
    PulseLoadingSpinnerButton,
    Modal,
    CollectionSearch,
  },
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      pageNumber: 0,
      searchQuery: '',
      searchText: '',
      searchChannels: '',
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      recipientBindings: [
        { referenceDisplayLabel: 'Recipient Full Name', apiName: 'full_name' },
        { referenceDisplayLabel: 'Recipient First Name', apiName: 'first_name' },
        { referenceDisplayLabel: 'Recipient Last Name', apiName: 'last_name' },
        { referenceDisplayLabel: 'Recipient Email', apiName: 'email' },
      ],
      alertRecipientOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'Owner', value: 'OWNER' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
        { key: 'Everyone', value: 'ALL' },
        { key: 'SDR', value: 'SDR' },
      ],
      alertTargetOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
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
      await this.listChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
    }
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
          this.fields.filters.salesforceObject = this.selectedResourceType
          this.fields.filters.page = 1
          await this.fields.refresh()
        }
      },
    },
  },
  methods: {
    async listChannels(cursor = null) {
      const res = await SlackOAuth.api.listChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.channelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.channelOpts = results
    },
    recipientTypeToggle(value) {
      if (!this.user.slackRef) {
        this.$Alert.alert({ type: 'error', message: 'Slack Not Integrated', timeout: 2000 })
        return 'USER_LEVEL'
      }
      if (value == 'USER_LEVEL') {
        return 'SLACK_CHANNEL'
      } else if (value == 'SLACK_CHANNEL') {
        return 'USER_LEVEL'
      }
      return value
    },
    accountResource() {
      this.alertTemplateForm.field.resourceType.value = 'Account'
    },
    leadResource() {
      this.alertTemplateForm.field.resourceType.value = 'Lead'
    },
    opportunityResource() {
      this.alertTemplateForm.field.resourceType.value = 'Opportunity'
    },

    async onSave() {
      this.savingTemplate = true
      this.alertTemplateForm.validate()
      if (this.alertTemplateForm.isValid) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate({
            ...this.alertTemplateForm.toAPI,
            user: this.$store.state.user.id,
          })
          this.$router.push({ name: 'ListTemplates' })
        } catch (e) {
          this.$Alert.alert({
            message: 'An error occured saving template',
            timeout: 2000,
            type: 'error',
          })
        } finally {
          this.savingTemplate = false
        }
      }
    },
    bindText(val) {
      this.$refs['message-body'].quill.focus()
      let start = 0
      if (this.editor.selection.lastRange) {
        start = this.editor.selection.lastRange.index
      }
      this.editor.insertText(start, `{ ${val} }`)
    },
    onNextPage() {
      this.pageNumber <= 2 ? (this.pageNumber += 1) : (this.pageNumber = this.pageNumber)
    },
    onPreviousPage() {
      this.pageNumber >= 1 ? (this.pageNumber -= 1) : (this.pageNumber = this.pageNumber)
    },
    setDay(obj) {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recurrenceDay.value = obj
    },
    setPipelines(obj) {
      this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.push(obj)
    },
    setRecipients(obj) {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value.push(obj)
    },
    setRecipient(obj) {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = obj
    },
    changeType(val) {
      this.recipientType = val
    },
    getListOfTargets(targets) {
      if (targets && targets.length) {
        return targets
          .map((opt) => {
            return opt.id == 'SELF' ? 'Your' : opt.fullName + "'s"
          })
          .join(', ')
      }
    },
    onAddAlertGroup() {
      // length determines order
      const order = this.alertTemplateForm.field.alertGroups.groups.length
      if (order >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 groups', timeout: 2000 })
        return
      }
      // set next order

      this.alertTemplateForm.addToArray('alertGroups', new AlertGroupForm())
      this.alertTemplateForm.field.alertGroups.groups[order].field.groupOrder.value = order
    },
    onAddAlertSetting() {
      if (this.alertTemplateForm.field.alertConfig.groups.length >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 configurations', timeout: 2000 })
        return
      }
      this.alertTemplateForm.addToArray('alertConfig', new AlertConfigForm())
    },
    onRemoveAlertGroup(i) {
      // get order and update options

      if (this.alertTemplateForm.field.alertGroups.groups.length - 1 <= 0) {
        return
      }

      const order = this.alertTemplateForm.field.alertGroups.groups[i].field.groupOrder.value

      this.alertTemplateForm.removeFromArray('alertGroups', i)

      let greaterThan = this.alertTemplateForm.field.alertGroups.groups.slice(i)

      greaterThan.forEach((el, index) => {
        el.field.groupOrder.value = order + index
      })
    },
    onRemoveSetting(i) {
      if (this.alertTemplateForm.field.alertConfig.groups.length - 1 <= 0) {
        return
      }
      this.alertTemplateForm.removeFromArray('alertConfig', i)
    },
    async onSearchFields(v) {
      this.fields.pagination = new Pagination()
      this.fields.filters = {
        ...this.fields.filters,
        search: v,
      }
      await this.fields.refresh()
    },
    async fieldNextPage() {
      await this.fields.addNextPage()
    },
    async onSearchUsers(v) {
      this.users.pagination = new Pagination()
      this.users.filters = {
        ...this.users.filters,
        search: v,
      }
      await this.users.refresh()
    },
    async onUsersNextPage() {
      await this.users.addNextPage()
    },
    showList() {
      this.listVisible = !this.listVisible
    },
    showDropDown() {
      this.dropdownVisible = !this.dropdownVisible
    },
  },
  computed: {
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
    filteredUserTargets() {
      if (this.searchQuery) {
        return this.userTargetsOpts.filter((key) => {
          return key.fullName.toLowerCase().startsWith(this.searchQuery.toLowerCase())
        })
      } else {
        return this.userTargetsOpts
      }
    },
    filteredRecipients() {
      if (this.searchText) {
        return this.recipientOpts.filter((key) => {
          return key.fullName.toLowerCase().startsWith(this.searchText.toLowerCase())
        })
      } else {
        return this.recipientOpts
      }
    },
    filteredChannels() {
      if (this.searchChannels) {
        return this.reversedChannels.filter((key) => {
          return key.name.toLowerCase().startsWith(this.searchChannels.toLowerCase())
        })
      } else {
        return this.reversedChannels
      }
    },
    recipientOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertRecipientOpts.map((opt) => {
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
    formValue() {
      return this.alertTemplateForm.value
    },
    reversedChannels() {
      return this.channelOpts.channels.reverse()
    },
    editor() {
      return this.$refs['message-body'].quill
    },
    selection() {
      return this.editor.selection.lastRange
    },
    alertObj() {
      return {
        title: this.formValue.title,
        message: this.formValue.alertMessages[0].body,
        resourceType: this.selectedResourceType,
      }
    },
    user() {
      return this.$store.state.user
    },
    selectedResourceType: {
      get() {
        return this.alertTemplateForm.field.resourceType.value
      },
      set(val) {
        this.alertTemplateForm.field.resourceType.value = val
      },
    },
  },
  beforeMount() {
    this.alertTemplateForm.field.resourceType.value = 'Opportunity'
    // this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
  },
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
  color: #4d4e4c;
  height: 2.5rem;
  background-color: #beb5cc;
  border: 1px solid #5d5e5e;
  width: 70%;
  // padding: 0 0 0 1rem;
  margin: 1rem;
  -webkit-box-shadow: 1px 4px 7px black;
  box-shadow: 1px 4px 7px black;
}
.bottom_locked {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: auto;
  margin-bottom: 0.5rem;
}
.remove__group {
  padding: 0.25rem;
  border-radius: 0.25rem;
  border: 2px solid $panther-gray;
  background-color: $panther-gray;
  display: flex;
  align-items: center;
  cursor: pointer;
}
.fixed__right {
  align-self: flex-end;
  margin-top: -2rem;
}
.message_titles {
  display: flex;
  align-items: center;
  flex-direction: column;
}
::v-deep .ql-toolbar .ql-stroke {
  fill: none;
  stroke: #fff;
}

::v-deep .ql-toolbar .ql-fill {
  fill: #fff;
  stroke: none;
}

::v-deep .ql-toolbar .ql-picker {
  color: #fff;
}

::v-deep .ql-editor.ql-blank::before {
  color: white;
}
::v-deep .collection-search__result-item {
  border: none;
  background-color: $panther;
}
::v-deep .input-content {
  width: 8vw;
  background-color: $panther-silver;
  color: $panther;
}
::v-deep .input-form__large {
  width: 8vw;
  background-color: $panther-silver;
  color: $panther;
}
::v-deep .collection-search .collection-search__form .collection-search__input .search__input {
  @include input-field();
  height: 2.5rem;
  background-color: $panther-silver;
  border: 1px solid $panther-gray;
  width: 10rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
  box-shadow: 1px 4px 7px black;
}
.filtered {
  filter: invert(40%) sepia(28%) saturate(6559%) hue-rotate(128deg) brightness(96%) contrast(80%);
}
.channels_height {
  height: 22vh;
  overflow-y: scroll;
}
.slack-form-builder {
  display: flex;
  flex-direction: column;
  position: relative;

  &__sf-fields,
  &__sf-validations {
    margin-right: 2rem;
  }

  &__container {
    display: flex;
    background-color: $panther;
  }

  &__sf-field {
    padding: 0.25rem;
    font-size: 0.85rem;
    font-weight: bold;
    font-display: #{$bold-font-family};
    background-color: $panther;
    &:hover {
      background-color: $panther;
      cursor: pointer;
      color: $panther-silver;
    }
  }

  &__required {
    padding: 0.25rem;
    font-size: 0.85rem;
    font-weight: bold;
    font-display: #{$bold-font-family};
    background-color: $panther;
    &:hover {
      background-color: $panther;
      cursor: pointer;
      color: $panther-orange;
    }
  }

  &__form {
    // flex: 10;
    width: 24vw;
    padding: 2rem;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    background-color: $panther;
    height: 50vh;
    overflow-y: scroll;
    overflow-x: hidden;
    border-radius: 0.5rem;
  }
}
.form-field {
  background-color: $panther;
  margin-top: 0.5rem;
  &__left {
    flex: 10;

    display: flex;
    align-items: center;
  }

  &__middle {
    flex: 2;

    display: flex;
    align-items: center;
  }

  &__body {
    font-size: 0.75rem;
  }

  &__label {
    font-weight: bold;
  }

  &__right {
    // flex: 2;
    display: flex;
    padding-left: 1rem;
    margin-right: -0.5rem;

    display: flex;
    align-items: center;
  }

  &__btn {
    padding: 0.35rem;
    cursor: pointer;
    color: $dark-gray-blue;

    transition: color 0.3s linear;

    &:hover {
      color: black;
    }

    &--flipped {
      transform: rotateX(180deg);
    }
  }
}
.message {
  width: 20vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.template__border {
  border-bottom: 2px solid $panther-silver;
}
.alert__column {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 0.5rem;
}
.alert__column__ {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 0.5rem;
}
.delivery__column {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.alert__row {
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.delivery__row {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
}
.sf__collection {
  display: flex;
  align-items: space-evenly;
  justify-content: center;
  flex-direction: column;
  background-color: $panther;
  border-radius: 0.4rem;
  height: 30vh;
  width: 60vw;
  margin-bottom: 1rem;
  padding: 1rem;
}
.collection__ {
  background-color: $panther;
  height: 30vh;
  width: 60vw;
  padding: 2rem;
  border-radius: 0.4rem;
}
.option__collection {
  background-color: $panther;
  justify-content: center;
  border-radius: 0.5rem;
  height: 34vh;
  width: 78vw;
  padding: 1rem;
}
.collection_fields {
  background-color: $panther;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 1rem;
  border-radius: 0.5rem;
  height: 46vh;
  width: 22vw;
  overflow-x: scroll;
}
.collection__fields {
  background-color: $panther;
  display: flex;
  justify-content: space-evenly;

  flex-direction: row;
  padding: 1rem;
  border-radius: 0.5rem;
  height: 48vh;
  width: 60vw;
  overflow-x: scroll;
}
.collection__fields__ {
  background-color: $panther;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: row;

  border-radius: 0.5rem;
  height: 50vh;
  width: 30vw;
  overflow-x: scroll;
}
.paginator {
  @include paginator();
  &__container {
    border: none;
    display: flex;
    justify-content: flex-start;
    width: 11rem;
    font-size: 0.75rem;
    margin-top: 1rem;
  }
  &__text {
    width: 6rem;
  }
}
.collection {
  background-color: $panther;
  height: 50vh;
  width: 30vw;
  padding: 2rem;

  border-radius: 0.25rem;
}
.alert_title {
  background-color: $panther;
  margin: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  width: 100%;
}
.alert__title {
  background-color: $panther;
  margin: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  width: 40%;
}
.space {
  height: 20vh;
}
.space__ {
  height: 16vh;
}
::-webkit-scrollbar {
  background-color: $panther;
  -webkit-appearance: none;
  width: 4px;
  height: 100%;
}
::-webkit-scrollbar-thumb {
  border-radius: 2px;
  background-color: $panther-silver;
}
.plus_button {
  border: none;
  background-color: $panther-silver;
  border-radius: 50%;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: bold;
}
.header {
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}
.remove_button {
  color: $panther-orange;
  border: none;
  font-weight: bold;
  background: transparent;
  cursor: pointer;
  margin: 0.25rem;
}
.quill-editor {
  width: 100%;
}

textarea {
  @extend .textarea;
}
.box__header {
  &__status {
    display: flex;
    &--error {
      color: $coral;
      fill: $coral;
    }
    &--success {
      color: $dark-green;
      fill: $dark-green;
    }
  }
}
.alerts-page {
  height: 88vh;
  color: white;
  margin-left: 12vw;
  margin-top: 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  &__previous-step {
    @include muted-font(12);
  }
  &__groups {
    &__group {
      display: flex;
    }
  }
  &__message {
    display: flex;
    height: 20rem;
    &-template {
      margin: 0rem 1rem;
      &__notification {
        width: 30rem;
        margin: 1rem 0rem;
      }
      &__message {
        width: 40rem;
        margin: 1rem 0rem;
      }
    }
  }
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  margin-top: 2rem;
}
.card__ {
  background-color: $panther;
  border: none;
  width: 10rem;
  min-height: 25vh;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 3px 4px 7px black;
  color: white;
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &header {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 5rem;
  }
}
.alerts-page__settings {
  display: flex;
  align-items: center;
  justify-content: space-evenly;

  &__frequency {
    display: flex;
    align-items: center;
    &-label {
      @include muted-font();
      margin: 0 0.5rem;
    }
  }
  &-remove {
    justify-self: end;
  }
}
.btn {
  &--danger {
    @include button-danger();
  }
  &--primary {
    @include primary-button();
  }
  &--secondary {
    @include secondary-button();
  }

  &--icon {
    @include --icon();
  }
}
.muted--link {
  @include muted-font();
  @include pointer-on-hover();
  &--important {
    color: red;
    font-weight: bold;
    font-size: 11px;
  }
}
.gray {
  color: $gray;
}
.slate {
  color: $slate-gray;
}
.pad {
  padding-bottom: 1rem;
  margin-top: -1rem;
}
.pink {
  color: $candy;
  font-weight: bold;
}
.purple {
  color: $grape;
  font-weight: bold;
}
.mar {
  margin-top: -2rem;
}
.center {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.sub {
  font-size: 12px;
  margin-left: 0.5rem;
}
.sub__ {
  font-size: 16px;
  margin-top: -0.5rem;
  color: $panther-silver;
}
.group {
  display: flex;
  flex-direction: row;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}
.byo__col {
  display: flex;
  flex-direction: column;
  align-items: center;
  align-self: center;
  color: white;
  background-color: $panther;
  border-radius: 0.5rem;
  width: 50vw;
  margin-top: 2rem;
}
.col__ {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;
}
.column {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.column__ {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 1rem;
  border-bottom: 3px solid $silver;
}
.row_ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  margin-top: 2rem;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-weight: bold;
}
.message__box {
  margin-bottom: 2rem;
  height: 24vh;
  width: 30vw;
}
.left {
  margin-bottom: 2rem;
}
.add__group {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 3rem;
  padding-bottom: 1rem;
  border-bottom: 3px solid $mid-gray;
}
.bolder {
  font-size: 16px;
  margin-left: 1rem;
  cursor: pointer;
  color: $base-gray;
}
.bolder:hover {
  border-bottom: 2px solid $candy;
  color: $candy;
}
.alertsModal {
  color: $candy;
  text-decoration: underline;
  cursor: pointer;
}
.modal__container {
  overflow-y: scroll;
}
.blue {
  color: $slate-gray;
}
.top {
  border-top: 3px solid $grape;
}
.templates {
  border-bottom: 1px solid $gray;
}
input {
  width: 130px;
  text-align: center;
  height: 36px;
  border-radius: 0.25rem;
  margin-top: 0.75rem;
  border: none;
  border-bottom: 1px solid $slate-gray;
  font-weight: bold;
}
.orange_button {
  width: 7rem;
  background-color: white;
  color: $panther-orange;
  font-weight: bold;
  font-size: 16px;
  height: 2rem;
  border-radius: 0.5rem;
  border: 2px solid white;
  cursor: pointer;
}
.gold__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $panther;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
}
.purple__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: $white;
  background-color: $dark-green;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
}
</style>
