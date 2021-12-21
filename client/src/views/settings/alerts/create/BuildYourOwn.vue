<template>
  <div class="alerts-page">
    <Modal style="margin-top: 8rem" ref="templateModal">
      <template v-slot:header>
        <h2 style="color: white">Popular Message Template</h2>
      </template>

      <template v-slot:body>
        <div>
          <div style="display: flex; flex-direction: row">
            <textarea
              style="height: 3rem; width: 90%; font-size: 0.75rem; margin-right: 0.25rem"
              name=""
              id=""
              cols="20"
              rows="10"
            >
          Hey { __Recipient.full_name }, your deal { Opportunity.Name } ...continue writing here
          </textarea
            >
            <button
              style="background-color: #3c3940; border: none; cursor: pointer"
              v-clipboard:copy="message"
              v-clipboard:success="onCopy"
              v-clipboard:error="onError"
            >
              <img src="@/assets/images/copy.png" style="height: 1rem" alt="" />
            </button>
          </div>
        </div>
      </template>
    </Modal>

    <div class="alert__row">
      <div v-if="pageNumber === 0" class="alert__column__" style="margin-bottom: 1rem">
        <h2 style="text-align: center; color: black; font-weight: bold">
          Create a Custom Workflow
        </h2>
        <div v-if="pageNumber === 0">
          <!-- <p style="text-align: center; border-bottom: 2px solid #beb5cc; padding-bottom: 0.25rem">
        Object Type
      </p> -->
          <h5
            style="text-align: center; margin-top: -1rem; margin-left: 0.5rem; color: black"
            class="title"
          >
            {{ alertTemplateForm.field.resourceType.value }} Selected. Switch to
            <span
              v-if="selectedResourceType === 'Opportunity'"
              v-on:click="accountResource"
              style="border-bottom: 3px solid #199e54; cursor: pointer"
              >Account</span
            >
            <span
              v-else
              v-on:click="opportunityResource"
              style="border-bottom: 3px solid #199e54; cursor: pointer"
              >Opporunity</span
            >
            or
            <span
              v-on:click="leadResource"
              style="border-bottom: 3px solid #199e54; cursor: pointer"
              >Lead</span
            >
          </h5>
        </div>
        <div
          style="
            margin: auto;
            text-align: center;
            width: 30%;
            margin-bottom: 1rem;
            margin-top: -0.5rem;
          "
          title="25.00%"
        >
          <div
            style="
              text-align: left;
              margin: 2px auto;
              font-size: 0px;
              line-height: 0px;
              border: solid 1px #aaaaaa;
              background: #0e572e;
              overflow: hidden;
              border-radius: 0.25rem;
            "
          >
            <div
              style="
                font-size: 0px;
                line-height: 0px;
                height: 6px;
                min-width: 0%;
                max-width: 25%;
                width: 25%;
                background: #199e54;
              "
            ></div>
          </div>
        </div>
        <div :key="index" v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups">
          <div class="sf__collection">
            <AlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />

            <p
              v-if="
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandIdentifier.value &&
                (alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  ._operandIdentifier.value.dataType === 'Date' ||
                  alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                    ._operandIdentifier.value.dataType === 'DateTime')
              "
              class="fixed__center"
            >
              We'll alert you if the
              {{
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandIdentifier.value
                  ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                      .field.operandIdentifier.value
                  : '___'
              }}
              is
              {{
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandOperator.value
                  ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                      .field._operandOperator.value.label
                  : '___'
              }}
              {{
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandValue.value
                  ? positiveDay(
                      alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                        .field.operandValue.value,
                    )
                  : '___'
              }}
            </p>

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
        <h2 style="text-align: center; color: black; font-weight: bold">Construct your Message</h2>
        <div
          style="margin: auto; text-align: center; width: 36%; margin-bottom: 1rem"
          title="25.00%"
        >
          <div
            style="
              text-align: left;
              margin: 2px auto;
              font-size: 0px;
              line-height: 0px;
              border: solid 1px #aaaaaa;
              background: #0e572e;
              overflow: hidden;
              border-radius: 0.25rem;
            "
          >
            <div
              style="
                font-size: 0px;
                line-height: 0px;
                height: 6px;
                min-width: 0%;
                max-width: 75%;
                width: 75%;
                background: #199e54;
              "
            ></div>
          </div>
        </div>
        <div class="collection__fields">
          <div class="message_titles">
            <p
              :class="templateBounce ? 'bouncy' : ''"
              @click="$refs.templateModal.openModal(), switchBounce()"
              style="cursor: pointer; border-bottom: 2px solid #199e54"
            >
              Popular Template
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
                    placeholder:
                      'Write your message from scratch, or build on top of the TEMPLATE...',
                    theme: 'snow',
                  }"
                  class="message__box"
                />
              </template>
            </FormField>
          </div>

          <div class="crm">
            <h4 style="margin-top: 2rem">Add CRM values</h4>
            <div @click="addCount()">
              <DropDownSearch
                :class="!templateBounce && fieldBounce && clickCount === 0 ? 'bouncy' : ''"
                :items="fields.list"
                @input="bindText(`${selectedResourceType}.${$event}`)"
                displayKey="referenceDisplayLabel"
                valueKey="apiName"
                nullDisplay="Search Fields"
                searchable
                :hasNext="!!fields.pagination.hasNextPage"
                @load-more="fieldNextPage"
                @search-term="onSearchFields"
                auto
              />
            </div>
          </div>
        </div>
      </div>

      <div v-if="pageNumber === 1" class="alert__column">
        <h2 style="text-align: center; color: black">Select Delivery Options</h2>
        <div
          style="margin: auto; text-align: center; width: 30%; margin-bottom: 1rem"
          title="25.00%"
        >
          <div
            style="
              text-align: left;
              margin: 2px auto;
              font-size: 0px;
              line-height: 0px;
              border: solid 1px #aaaaaa;
              background: #0e572e;
              overflow: hidden;
              border-radius: 0.25rem;
            "
          >
            <div
              style="
                font-size: 0px;
                line-height: 0px;
                height: 6px;
                min-width: 0%;
                max-width: 50%;
                width: 50%;
                background: #199e54;
              "
            ></div>
          </div>
        </div>
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
                  padding: 0.5rem;
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
                          @input="form.field.recurrenceDay.validate()"
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
                    v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
                    placeholder="Day of month"
                    :errors="form.field.recurrenceDay.errors"
                    @blur="form.field.recurrenceDay.validate()"
                    v-model="form.field.recurrenceDay.value"
                    small
                  />

                  <p
                    @click="removeDay"
                    v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
                    :class="form.field.recurrenceDay.value ? 'selected__item' : 'visible'"
                  >
                    <img
                      src="@/assets/images/remove.png"
                      style="height: 1rem; margin-right: 0.25rem"
                      alt=""
                    />
                    {{ form.field.recurrenceDay.value }}
                  </p>

                  <p
                    @click="removeDay"
                    v-else-if="form.field.recurrenceFrequency.value == 'WEEKLY'"
                    :class="form.field.recurrenceDay.value ? 'selected__item' : 'visible'"
                  >
                    <img
                      src="@/assets/images/remove.png"
                      style="height: 1rem; margin-right: 0.25rem"
                      alt=""
                    />
                    {{ convertToDay(form.field.recurrenceDay.value) }}
                  </p>
                </div>
              </div>

              <div
                v-if="user.userLevel == 'MANAGER'"
                style="
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: space-evenly;
                  padding: 0.5rem;
                "
              >
                <span style="font-weight: bold; margin-bottom: 0.3rem">Select pipelines</span>
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
                      @input="form.field.alertTargets.validate()"
                      displayKey="fullName"
                      valueKey="id"
                      nullDisplay="Mulit-select"
                      searchable
                      multi
                      medium
                      :loading="users.loadingNextPage"
                      :hasNext="!!users.pagination.hasNextPage"
                      @load-more="onUsersNextPage"
                      @search-term="onSearchUsers"
                    />
                  </template>
                </FormField>
                <div style="margin-top: -0.5rem" class="items_height">
                  <p
                    :key="i"
                    v-for="(item, i) in form.field.alertTargets.value"
                    :class="form.field.alertTargets.value ? 'selected__item' : ''"
                    @click="removeItemFromTargetArray(item)"
                  >
                    <img
                      src="@/assets/images/remove.png"
                      style="height: 1rem; margin-right: 0.25rem"
                      alt=""
                    />
                    {{ item.length ? item : '' }}
                  </p>
                </div>
              </div>

              <div
                style="
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: flex-start;
                  padding: 0.5rem;
                "
              >
                <div v-if="!channelName" class="row__">
                  <label>Select #channel</label>
                  <ToggleCheckBox
                    style="margin: 0.25rem"
                    @input="changeCreate"
                    :value="create"
                    offColor="#199e54"
                    onColor="#199e54"
                  />
                  <label>Create #channel</label>
                </div>

                <label v-else for="channel" style="font-weight: bold"
                  >Alert will send to
                  <span style="color: #199e54; font-size: 1.2rem">{{ channelName }}</span>
                  channel</label
                >
                <div
                  style="
                    display: flex;
                    flex-direction: column;
                    align-items: center;
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

                  <div v-if="!channelCreated" v style="margin-top: 1.25rem">
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

                <div v-else>
                  <FormField>
                    <template v-slot:input>
                      <DropDownSearch
                        :items.sync="userChannelOpts.channels"
                        :itemsRef.sync="form.field._recipients.value"
                        v-model="form.field.recipients.value"
                        @input="form.field.recipients.validate()"
                        displayKey="name"
                        valueKey="id"
                        nullDisplay="Channels"
                        :hasNext="!!userChannelOpts.nextCursor"
                        @load-more="listChannels(userChannelOpts.nextCursor)"
                        searchable
                        local
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

                  <p
                    v-if="form.field.recipients.value.length > 0"
                    @click="removeTarget"
                    :class="form.field.recipients.value ? 'selected__item' : 'visible'"
                  >
                    <img
                      src="@/assets/images/remove.png"
                      style="height: 1rem; margin-right: 0.25rem"
                      alt=""
                    />
                    {{ form.field._recipients.value.name }}
                  </p>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div class="alert__column" v-if="pageNumber === 3">
        <h2 style="text-align: center; color: black; font-weight: bold">
          Name your Alert, Review, and Save
        </h2>
        <div
          style="margin: auto; text-align: center; width: 65%; margin-bottom: 1rem"
          title="25.00%"
        >
          <div
            style="
              text-align: left;
              margin: 2px auto;
              font-size: 0px;
              line-height: 0px;
              border: solid 1px #aaaaaa;
              background: #0e572e;
              overflow: hidden;
              border-radius: 0.25rem;
            "
          >
            <div
              style="
                font-size: 0px;
                line-height: 0px;
                height: 6px;
                min-width: 0%;
                max-width: 100%;
                width: 100%;
                background: #199e54;
              "
            ></div>
          </div>
        </div>
        <template>
          <div
            style="
              display: flex;
              justify-content: center;
              align-items: center;
              flex-direction: column;
            "
            class="collection__small"
          >
            <h2>
              {{ alertTemplateForm.field.title.value ? alertTemplateForm.field.title.value : '' }}
            </h2>
            <FormField
              id="alert-title"
              v-model="alertTemplateForm.field.title.value"
              placeholder="Name your alert"
              :errors="alertTemplateForm.field.title.errors"
              @blur="alertTemplateForm.field.title.validate()"
            />
            <!-- <AlertSummary :form="alertTemplateForm" /> -->
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
      <div v-if="pageNumber < 3">
        <div v-if="pageNumber === 0">
          <button
            v-if="
              !alertTemplateForm.field.alertGroups.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            @click="onNextPage"
            class="purple__button"
          >
            Next
          </button>
          <div class="tooltip" v-else>
            <button class="disabled__button tooltip__icon">Next</button>
            <div class="tooltip__popup">
              <div class="tip">Complete this section to continue.</div>
            </div>
          </div>
        </div>

        <div v-if="pageNumber === 1">
          <button
            v-if="
              !alertTemplateForm.field.alertConfig.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            @click="onNextPage"
            class="purple__button"
          >
            Next
          </button>
          <div class="tooltip" v-else>
            <button class="disabled__button tooltip__icon">Next</button>
            <div class="tooltip__popup">
              <div class="tip">Complete this section to continue.</div>
            </div>
          </div>
        </div>
        <div v-if="pageNumber === 2">
          <button
            v-if="
              !alertTemplateForm.field.alertMessages.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            @click="onNextPage"
            class="purple__button"
          >
            Next
          </button>
          <div class="tooltip" v-else>
            <button class="disabled__button tooltip__icon">Next</button>
            <div class="tooltip__popup">
              <div class="tip">Complete this section to continue.</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <PulseLoadingSpinnerButton
          v-if="alertTemplateForm.isValid || savingTemplate"
          :loading="savingTemplate"
          class="purple__button"
          text="Save Alert"
          @click.stop="onSave"
        />

        <div class="tooltip" v-else>
          <button class="disabled__button tooltip__icon">Save Alert</button>
          <div class="tooltip__popup">
            <div class="tip">Alert title required.</div>
          </div>
        </div>
      </div>
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
import ProgressBar from '@/components/ProgressBar'
import CheckBox from '@/components/CheckBoxUpdated'

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
    ProgressBar,
    CheckBox,
  },
  data() {
    return {
      channelOpts: new SlackListResponse(),
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      message: 'Hey { __Recipient.full_name }, your deal { Opportunity.Name }',
      templateBounce: true,
      fieldBounce: true,
      clickCount: 0,
      newChannel: {},
      showMenu: true,
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
      create: true,
      channelCreated: false,
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
      await this.listUserChannels()
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
    positiveDay(num) {
      if (num < 0) {
        return (num *= -1) + ' days before your selected delivery day.'
      } else if (num == 0) {
        return ' the day of your selected delivery day.'
      } else {
        return num + ' days away from your selected delivery day.'
      }
    },
    repsPipeline() {
      if (this.user.userLevel == 'REP') {
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.push('SELF')
        this.setPipelines({
          fullName: 'MYSELF',
          id: 'SELF',
        })
      }
    },
    switchBounce() {
      this.templateBounce = !this.templateBounce
    },
    addCount() {
      this.clickCount += 1
    },
    onCopy: function () {
      this.$Alert.alert({
        message: 'Message Copied to clipboard successfully',
        type: 'success',
        timeout: 2000,
      })
    },
    onError: function () {
      this.$Alert.alert({
        message: 'error copying template',
        type: 'error',
        timeout: 2000,
      })
    },
    changeCreate() {
      this.create = !this.create
      if (
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value !==
        'SLACK_CHANNEL'
      ) {
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value =
          'SLACK_CHANNEL'
      }
    },
    async listChannels(cursor = null) {
      const res = await SlackOAuth.api.listChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.channelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.channelOpts = results
    },
    async listUserChannels(cursor = null) {
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
    },
    async createChannel(name) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = res.channel
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = res.channel.id
        this.channelCreated = !this.channelCreated
      } else {
        console.log(res.error)
        this.channelName = ''
        if (res.error == 'name_taken') {
          this.$Alert.alert({
            message: 'Channel name already taken',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name_maxlength') {
          this.$Alert.alert({
            message: 'Channel name exceeds maximum length',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'restricted_action') {
          this.$Alert.alert({
            message: 'A team preference is preventing you from creating channels',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name_specials') {
          this.$Alert.alert({
            message:
              'The only special characters allowed are hyphens and underscores. Channel names must also begin with a letter ',
            type: 'error',
            timeout: 3000,
          })
        } else if (res.error == 'org_login_required') {
          this.$Alert.alert({
            message:
              'The workspace is undergoing an enterprise migration and will not be available until migration is complete.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'ekm_access_denied') {
          this.$Alert.alert({
            message: 'Administrators have suspended the ability to post a message.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'too_many_convos_for_team') {
          this.$Alert.alert({
            message: 'The workspace has exceeded its limit of public and private channels.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'no_permission') {
          this.$Alert.alert({
            message:
              'The workspace token used in this request does not have the permissions necessary to complete the request. Make sure your app is a member of the conversation its attempting to post a message to.',
            type: 'error',
            timeout: 4000,
          })
        } else if (res.error == 'team_access_not_granted') {
          this.$Alert.alert({
            message:
              'You are not granted the specific workspace access required to complete this request.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name') {
          this.$Alert.alert({
            message: 'Channel name invalid. Please try again',
            type: 'error',
            timeout: 2000,
          })
        } else {
          this.$Alert.alert({
            message: 'Something went wrong..Please try again',
            type: 'error',
            timeout: 2000,
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
    removeDay() {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDay.value = ''
    },
    removeTarget() {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = []
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = []
    },
    removeItemFromTargetArray(item) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value =
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.filter(
          (i) => i !== item,
        )
    },
    removeItemFromRecipientArray(item) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value =
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value.filter(
          (i) => i !== item,
        )
    },
    // showRecipientValue(val){
    //   if(this.alertTemplateForm.field.recipients.value.length > 0){

    //   }
    // },
    convertToDay(num) {
      if (num == 0) {
        return 'Monday'
      } else if (num == 1) {
        return 'Tuesday'
      } else if (num == 2) {
        return 'Wednesday'
      } else if (num == 3) {
        return 'Thursday'
      } else if (num == 4) {
        return 'Friday'
      } else if (num == 5) {
        return 'Saturday'
      } else if (num == 6) {
        return 'Sunday'
      }
    },
    recipientTypeToggle(value) {
      if (!this.user.slackRef) {
        this.$Alert.alert({ type: 'error', message: 'Slack Not Integrated', timeout: 2000 })
        return 'USER_LEVEL'
      }
      if (value == 'USER_LEVEL') {
        return 'SLACK_CHANNEL'
      } else if (value == 'SLACK_CHANNEL') {
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = []
        this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = []
        return 'USER_LEVEL'
      }
      return value
    },
    onMenuShow() {
      this.showMenu = !this.showMenu
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
    this.repsPipeline()
    this.alertTemplateForm.field.isActive.value = true
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

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
::placeholder {
  color: $panther-silver;
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
  border: 1px solid #5d5e5e;
  width: 70%;
  // padding: 0 0 0 1rem;

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
.object-selection {
  z-index: 10;
  position: absolute;
  right: 0;
  padding: 0.75rem;
  width: 18vw;
  background-color: $panther;
  border-radius: 0.5rem;
  box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
}
.show_menu {
  margin-right: 0.25rem;
  margin-top: 0.25rem;
  cursor: pointer;
}
.hide {
  display: none;
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
  border: 1px solid red;
}
.fixed__center {
  align-self: center;
  color: $panther-silver;
}
.message_titles {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.crm {
  display: flex;
  align-items: center;
  flex-direction: column;
}
::v-deep .ql-toolbar .ql-stroke {
  fill: none;
  stroke: $panther;
}

::v-deep .ql-toolbar .ql-fill {
  fill: $panther;
  stroke: none;
}

::v-deep .ql-toolbar .ql-picker {
  color: $panther;
}

::v-deep .ql-editor.ql-blank::before {
  color: $panther;
}
::v-deep .ql-container.ql-snow {
  border-radius: 0.3rem;
  border: 3px solid $panther-silver;
}
::v-deep .ql-toolbar.ql-snow {
  border-radius: 0.3rem;
  border: 3px solid $panther-silver;
  border-bottom: 2px solid $panther-silver;
  background-color: white;
  margin-bottom: 0.1rem;
}
::v-deep .ql-blank.ql-editor {
  background-color: white;
  border-radius: 0.3rem;
}
::v-deep .ql-container {
  background-color: white;
  color: $panther;
}
::v-deep .collection-search__result-item {
  border: none;
  background-color: $panther;
}
::v-deep .input-content {
  width: 12vw;
  background-color: white;
  color: $panther;
}
::v-deep .input-form__large {
  width: 12vw;
  background-color: white;
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
.fields_height {
  height: 30vh;
  overflow-y: scroll;
}
.items_height {
  overflow-y: scroll;
  max-height: 30vh;
  width: 100%;
}
.recipients_height {
  overflow-y: scroll;
  max-height: 30vh;
  width: 80%;
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
  align-items: flex-start;
}
.sf__collection {
  display: flex;
  align-items: space-evenly;
  justify-content: center;
  flex-direction: column;
  background-color: $panther;
  border-radius: 0.75rem;

  width: 75vw;
  padding: 2rem;
  margin-bottom: 1rem;
}
.collection__ {
  background-color: $panther;
  width: 75vw;
  padding: 2rem;
  border-radius: 0.75rem;
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
  height: 46vh;
  width: 70vw;
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
  height: 60vh;
  width: 30vw;
  padding: 2rem;
  border-radius: 0.33rem;
}
.collection__small {
  background-color: $panther;
  height: 30vh;
  width: 30vw;
  padding: 2rem;
  border-radius: 0.33rem;
}
.alert_title {
  background-color: $panther;
  margin: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  width: 30%;
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
// ::-webkit-scrollbar {
//   background-color: $panther;
//   -webkit-appearance: none;
//   width: 4px;
//   height: 100%;
// }
// ::-webkit-scrollbar-thumb {
//   border-radius: 2px;
//   background-color: $panther-silver;
// }
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
  margin-left: 18vw;
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
  width: 32vw;
  border-radius: 0.25rem;
  background-color: transparent;
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
.tooltip {
  position: relative;
  &__icon {
    height: 2rem;
  }

  &__popup {
    width: 18rem;
    visibility: hidden;

    padding: 13px 21px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    border: solid 2px $panther-gray;
    background-color: $panther;
    color: white;
    position: absolute;
    bottom: -5px;
    left: 105%;

    &__bold {
      font-family: #{$bold-font-family};
      color: $panther-silver;
    }
  }
}

.tooltip:hover .tooltip__popup {
  visibility: visible;
}
.selected__item {
  padding: 0.5rem;
  border: 2px solid white;
  border-radius: 0.3rem;
  width: 100%;
  text-align: center;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}
.visible {
  display: none;
}
</style>