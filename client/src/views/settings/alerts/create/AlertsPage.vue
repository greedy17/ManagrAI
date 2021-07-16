<template>
  <div class="alerts-page">
    <ExpandablePanel>
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span class="gray">
            {{
              selectedResourceType
                ? selectedResourceType
                : "Select the Salesforce Object you'd like to build an alert for"
            }}
          </span>

          <span
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
            v-if="alertTemplateForm.field.resourceType.isValid"
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <FormField :errors="alertTemplateForm.field.resourceType.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="SOBJECTS_LIST"
              :itemsRef.sync="alertTemplateForm.field._resourceType.value"
              v-model="alertTemplateForm.field.resourceType.value"
              displayKey="key"
              valueKey="value"
              nullDisplay="Salesforce Objects"
              searchable
              local
              @input="alertTemplateForm.field.resourceType.validate()"
            />
          </template>
        </FormField>
      </template>
    </ExpandablePanel>
    <ExpandablePanel v-if="alertTemplateForm.field.resourceType.isValid">
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span class="gray">
            {{
              selectedResourceType ? `Build your ${selectedResourceType} alert` : 'Build alert'
            }}</span
          ><span
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
            v-if="
              alertTemplateForm.field.title.isValid &&
              !alertTemplateForm.field.alertGroups.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <FormField
            id="alert-title"
            v-model="alertTemplateForm.field.title.value"
            placeholder="Alert Title (required)"
            :errors="alertTemplateForm.field.title.errors"
            @blur="alertTemplateForm.field.title.validate()"
          />
          <div
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
            class="alerts-page__groups__group"
          >
            <AlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />

            <div>
              <button
                class="btn btn--danger btn--icon"
                @click.stop="onRemoveAlertGroup(index)"
                :disabled="alertTemplateForm.field.alertGroups.groups.length - 1 <= 0"
              >
                <svg width="24px" height="24px" viewBox="0 0 24 24">
                  <use xlink:href="@/assets/images/remove.svg#remove" />
                </svg>
              </button>
            </div>
          </div>
          <button class="btn btn--secondary btn--icon" @click="onAddAlertGroup">
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
            </svg>
          </button>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel
      v-if="
        alertTemplateForm.field.title.isValid &&
        !alertTemplateForm.field.alertGroups.groups.map((fields) => fields.isValid).includes(false)
      "
    >
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span class="gray">Construct Message </span>

          <span
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
            v-if="
              !alertTemplateForm.field.alertMessages.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div class="alerts-page__message">
            <div class="alerts-page__message-options">
              <FormField
                v-model="
                  alertTemplateForm.field.alertMessages.groups[0].field.notificationText.value
                "
                id="notification-text"
                large
                placeholder="Snippet in slack notification"
              />
              <div class="alerts-page__message-options-body" style="height: 5rem; width: 30rem">
                <FormField
                  :errors="alertTemplateForm.field.alertMessages.groups[0].field.body.errors"
                >
                  <template v-slot:input>
                    <quill-editor
                      @blur="alertTemplateForm.field.alertMessages.groups[0].field.body.validate()"
                      ref="message-body"
                      v-model="alertTemplateForm.field.alertMessages.groups[0].field.body.value"
                      :options="{
                        modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                      }"
                    />
                  </template>
                </FormField>
                <div class="alerts-page__message-options-body__bindings">
                  <div class="alerts-page__message-options-body__bindings__fields">
                    <DropDownSearch
                      :items="fields.list"
                      @input="bindText(`${selectedResourceType}.${$event}`)"
                      displayKey="referenceDisplayLabel"
                      valueKey="apiName"
                      nullDisplay="Select a field"
                      searchable
                      :hasNext="!!fields.pagination.hasNextPage"
                      @load-more="fieldNextPage"
                      @search-term="onSearchFields"
                      auto
                    />
                  </div>
                  <ListContainer horizontal>
                    <template v-slot:list>
                      <ListItem
                        :key="key"
                        v-for="(val, key) in recipientBindings"
                        :item="val.referenceDisplayLabel"
                        :active="true"
                        @item-selected="bindText(`__Recipient.${val.apiName}`)"
                      />
                    </template>
                  </ListContainer>
                </div>
              </div>
            </div>
            <div class="alerts-page__message-template">
              <div class="alerts-page__message-template__notification">
                <SlackNotificationTemplate
                  :msg="
                    alertTemplateForm.field.alertMessages.groups[0].field.notificationText.value
                  "
                />
              </div>
              <div class="alerts-page__message-template__message">
                <SlackMessagePreview :alert="alertObj" />
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel
      v-if="
        !alertTemplateForm.field.alertMessages.groups
          .map((fields) => fields.isValid)
          .includes(false)
      "
    >
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span class="gray"> Alert Settings </span><span> </span>
          <span
            v-if="
              !alertTemplateForm.field.alertConfig.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div
            class="alerts-page__settings"
            :key="i"
            v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
          >
            <div class="alerts-page__settings__frequency">
              <label class="alerts-page__settings__frequency-label">Weekly</label>
              <ToggleCheckBox
                @input="
                  form.field.recurrenceFrequency.value == 'WEEKLY'
                    ? (form.field.recurrenceFrequency.value = 'MONTHLY')
                    : (form.field.recurrenceFrequency.value = 'WEEKLY')
                "
                :value="form.field.recurrenceFrequency.value !== 'WEEKLY'"
                offColor="#199e54"
                onColor="#199e54"
              />
              <label class="alerts-page__settings__frequency-label">Monthly</label>
            </div>
            <div class="alerts-page__settings__day">
              <FormField
                v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
                placeholder="Day of month"
                :errors="form.field.recurrenceDay.errors"
                @blur="form.field.recurrenceDay.validate()"
                v-model="form.field.recurrenceDay.value"
                small
              />
              <FormField
                v-else-if="form.field.recurrenceFrequency.value == 'WEEKLY'"
                :errors="form.field.recurrenceDay.errors"
              >
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="weeklyOpts"
                    :itemsRef.sync="form.field._recurrenceDay.value"
                    v-model="form.field.recurrenceDay.value"
                    @input="form.field.recurrenceDay.validate()"
                    displayKey="key"
                    valueKey="value"
                    nullDisplay="Select"
                    searchable
                    local
                  />
                </template>
              </FormField>
            </div>
            <div class="alerts-page__settings__recipients">
              <span
                v-if="
                  form.field._recipients.value && form.field.recipientType.value == 'SLACK_CHANNEL'
                "
                class="muted--link--important"
              >
                Please make sure @managr has been added to
                <em>{{ form.field._recipients.value.name }}</em> channel
              </span>
              <FormField
                v-if="form.field.recipientType.value == 'USER_LEVEL'"
                :errors="form.field.recipients.errors"
              >
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="alertRecipientOpts"
                    :itemsRef.sync="form.field._recipients.value"
                    v-model="form.field.recipients.value"
                    @input="form.field.recipients.validate()"
                    displayKey="key"
                    valueKey="value"
                    nullDisplay="User groups"
                    searchable
                    local
                  />
                </template>
              </FormField>
              <FormField
                v-if="form.field.recipientType.value == 'SLACK_CHANNEL'"
                :errors="form.field.recipients.errors"
              >
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="channelOpts.channels"
                    :itemsRef.sync="form.field._recipients.value"
                    v-model="form.field.recipients.value"
                    @input="form.field.recipients.validate()"
                    displayKey="name"
                    valueKey="id"
                    nullDisplay="Channels"
                    :hasNext="!!channelOpts.nextCursor"
                    @load-more="listChannels(channelOpts.nextCursor)"
                  >
                    <template v-slot:tn-dropdown-option="{ option }">
                      <img
                        v-if="option.isPrivate == true"
                        class="card-img"
                        style="width: 1rem; height: 1rem; margin-right: 0.2rem"
                        src="@/assets/images/lockAsset.png"
                      />
                      {{ option['name'] }}
                    </template>
                  </DropDownSearch>
                </template>
              </FormField>
            </div>
            <div class="alerts-page__settings__recipient-type">
              <span
                @click="
                  form.field.recipientType.value = recipientTypeToggle(
                    form.field.recipientType.value,
                  )
                "
                class="muted--link"
                v-if="form.field.recipientType.value == 'USER_LEVEL'"
                >Send to a channel instead ?</span
              >

              <span
                @click="
                  form.field.recipientType.value = recipientTypeToggle(
                    form.field.recipientType.value,
                  )
                "
                class="muted--link"
                v-else
              >
                Send to a group of users (DM) instead ?
              </span>
            </div>
            <div class="alerts-page__settings-remove">
              <button
                class="btn btn--danger btn--icon"
                @click.stop="onRemoveSetting(i)"
                :disabled="alertTemplateForm.field.alertConfig.groups.length - 1 <= 0"
              >
                <svg width="24px" height="24px" viewBox="0 0 24 24">
                  <use xlink:href="@/assets/images/remove.svg#remove" />
                </svg>
              </button>
            </div>
          </div>
          <button class="btn btn--secondary btn--icon" @click="onAddAlertSetting">
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
            </svg>
          </button>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel
      class="gray"
      title="Preview Alert Configuration"
      v-if="
        !alertTemplateForm.field.alertConfig.groups.map((fields) => fields.isValid).includes(false)
      "
    >
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <AlertSummary :form="alertTemplateForm" />
          <PulseLoadingSpinnerButton
            :loading="savingTemplate"
            class="primary-button"
            text="Save"
            @click.stop="onSave"
            :disabled="!alertTemplateForm.isValid || savingTemplate"
          />
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
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
import {
  SObjectField,
  SObjectValidations,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
} from '@/services/salesforce'
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
  },
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      fields: CollectionManager.create({ ModelClass: SObjectField }),
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
    async onSave() {
      this.savingTemplate = true
      this.alertTemplateForm.validate()
      if (this.alertTemplateForm.isValid) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate(this.alertTemplateForm.toAPI)
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
  },
  computed: {
    formValue() {
      return this.alertTemplateForm.value
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
.alerts-page__message-options-body__bindings__fields {
  margin: 2rem 0rem;
  width: 20rem;
}
.gray {
  color: $gray;
  text-align: center;
}
</style>
