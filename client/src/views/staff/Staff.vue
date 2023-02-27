<template>
  <div class="staff">
    <!-- Change Admin Confirmation -->
    <Modal
      v-if="changeAdminConfirmModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleConfirmCancel()
        }
      "
    >
      <form v-if="true /*hasSlack*/" class="invite-form modal-form confirm-form form-margin-small">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Are you sure?</h3>
          </div>
          <div class="flex-row">
            <h4 @click="test(orgUsers)" class="invite-form__subtitle">
              By clicking Confirm, you will be transferring the Admin role to
              {{ this.newAdmin ? this.newAdmin.email : 'the selected user' }}.
            </h4>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="changeAdminSubmit"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <Modal v-if="deleteOpen">
      <div class="delete_modal">
        <div class="delete_modal__header">
          <h4>Delete Org</h4>
          <img
            @click="deleteOpen = !deleteOpen"
            src="@/assets/images/close.svg"
            height="22px"
            alt=""
          />
        </div>

        <div class="delete_modal__body">
          <p>This can't be reversed. Are you sure?</p>
        </div>

        <div class="delete_modal__footer">
          <button class="no__button" @click="deleteClose">Cancel</button>
          <button class="delete" @click.stop="onDeleteOrg">Delete</button>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="editOpModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetEdit()
        }
      "
    >
      <div class="modal-container" v-if="modalInfo">
        <div v-if="modalName === 'task'">
          <h2 class="modal-container__header">{{ modalInfo.fields.task_name }}</h2>
          <div class="modal-container__body">
            <div class="" style="margin-bottom: 1rem">
              <div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Task Params:</span>
                  {{ modalInfo.fields.task_params ? modalInfo.fields.task_params : 'Null' }}
                </div>
                <div>
                  <span class="">Task Hash:</span>
                  {{ modalInfo.fields.task_hash ? modalInfo.fields.task_hash : 'Null' }} |
                </div>
                <div>
                  <span class="">Verbose Name:</span>
                  {{ modalInfo.fields.verbose_name ? modalInfo.fields.verbose_name : 'Null' }} |
                </div>
                <div>
                  <span class="">Priority:</span>
                  {{
                    modalInfo.fields.priority || modalInfo.fields.priority === 0
                      ? modalInfo.fields.priority
                      : 'Null'
                  }}
                  |
                  <span class="">Run At:</span>
                  {{ modalInfo.fields.run_at ? modalInfo.fields.run_at : 'Null' }} |
                  <span class="">Repeat:</span>
                  {{
                    modalInfo.fields.repeat || modalInfo.fields.repeat === 0
                      ? modalInfo.fields.repeat
                      : 'Null'
                  }}
                  |
                  <span class="">Repeat Until:</span>
                  {{ modalInfo.fields.repeat_until ? modalInfo.fields.repeat_until : 'Null' }} |
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Queue:</span>
                  {{ modalInfo.fields.queue ? modalInfo.fields.queue : 'Null' }} |
                  <span class="">Attempts:</span>
                  {{ modalInfo.fields.attempts }}
                </div>
              </div>
              <div v-if="modalInfo.fields.failed_at">
                <div class="separator"></div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Failed At:</span>
                  {{ modalInfo.fields.failed_at ? modalInfo.fields.failed_at : 'Null' }}
                </div>
                <div style="margin-bottom: 0.5rem; color: #fa646a">
                  <span class="" style="color: black">Last Error:</span>
                  <div style="margin-left: 0.5rem">
                    {{ modalInfo.fields.last_error ? modalInfo.fields.last_error : 'Null' }}
                  </div>
                </div>
              </div>
              <div class="separator"></div>
              <div>
                <span class="">Locked By:</span>
                {{ modalInfo.fields.locked_by ? modalInfo.fields.locked_by : 'Null' }} |
                <span class="">Locked At:</span>
                {{ modalInfo.fields.locked_at ? modalInfo.fields.locked_at : 'Null' }} |
              </div>
              <div>
                <span class="">Creator Content Type:</span>
                {{
                  modalInfo.fields.creator_content_type
                    ? modalInfo.fields.creator_content_type
                    : 'Null'
                }}
                |
                <span class="">Creator Object ID:</span>
                {{
                  modalInfo.fields.creator_object_id ? modalInfo.fields.creator_object_id : 'Null'
                }}
              </div>
            </div>
          </div>
        </div>
        <div v-if="modalName === 'slackForm'">
          <div class="modal-container__body">
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>{{ modalInfo.form_type }} {{ modalInfo.resource }}</h4>
              </div>
            </div>
            <section
              class="note-section__body"
              style="margin-top: 1rem; margin-bottom: 1rem; white-space: normal; padding-left: 20px"
            >
              <!-- <div>{{modalInfo}}</div> -->
              <div v-for="(field, i) in modalInfo.fields_ref" :key="field.field">
                <div style="margin-top: 0.5rem; margin-bottom: 0.5rem">
                  {{ i + 1 }}.) {{ field.field_ref.label }} ({{ field.field_ref.api_name }})
                </div>
              </div>
            </section>
            <!-- <h2>{{ selectedSlackForms.form_type }} {{ selectedSlackForms.resource }}</h2> -->
            <!-- <div class="note-section" v-for="(field, i) in selectedSlackForms.fields_ref" :key="field.field">
              <div style="margin-bottom: 1rem">
                {{ i + 1 }} | {{ field.field_ref.label }} ({{ field.field_ref.api_name }})
              </div>
            </div> -->
          </div>
        </div>
        <div v-if="modalName === 'slackFormInstance'">
          <div class="modal-container__body">
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>
                  {{ modalInfo.template_ref ? modalInfo.template_ref.resource : '--' }}
                  {{ modalInfo.template_ref ? modalInfo.template_ref.form_type : '' }} by
                  {{ getUserName(modalInfo.user) }}
                </h4>
              </div>
            </div>
            <section class="note-section">
              <p class="note-section__title">
                Resource: {{ modalInfo.resource_id ? modalInfo.resource_id : 'N/A' }}
              </p>
              <p class="note-section__date">
                {{
                  modalInfo.submissionDate
                    ? `Submitted on ${weekDay(modalInfo.submission_date)} ${formatDateTime(
                        modalInfo.submission_date,
                      )}`
                    : 'Not Submitted'
                }}
              </p>
              <div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Workflow ID:</span>
                  {{ modalInfo.workflow ? modalInfo.workflow : 'None' }} |
                  <span class="">Update Source:</span>
                  {{ modalInfo.update_source ? modalInfo.update_source : 'None' }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">User ID:</span>
                  {{ modalInfo.user ? modalInfo.user : 'None' }} |
                  <span class="">Template ID:</span>
                  {{ modalInfo.template ? modalInfo.template : 'None' }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Saved Data:</span>
                  <!-- {{ modalInfo.saved_data ? modalInfo.saved_data : 'None' }} -->
                  <div v-for="(value,propertyName) in modalInfo.saved_data" :key="value" style="margin-left: 1rem;">
                    {{propertyName}}: <span 
                    @click="test(modalInfo.previous_data[propertyName] !== value)" 
                    :class="
                    modalInfo.previous_data[propertyName] === undefined
                    ||
                    (modalInfo.previous_data[propertyName] !== value && (Number(modalInfo.previous_data[propertyName]) && (modalInfo.previous_data[propertyName].toString().split('.')[1] === undefined || !checkDecimals(modalInfo.previous_data[propertyName])) ? checkDecimals(value): true))
                    ? 'yellow-background' : ''"
                    >{{ `${value}` }}</span>
                  </div>
                </div>
                <div>
                  <span class="">Previous Data:</span>
                  <div
                    v-for="(value, propertyName) in modalInfo.previous_data"
                    :key="value"
                    style="margin-left: 1rem"
                  >
                    {{ propertyName }}:
                    <span @click="test(modalInfo.saved_data[propertyName] !== value)" :class="''">{{
                      `${value}`
                    }}</span>
                    <!-- (
                      modalInfo.saved_data[propertyName] && 
                      modalInfo.saved_data[propertyName] !== value
                    ) ? 'yellow-background' : '' -->
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
        <div v-else-if="modalName === 'meetingWorkflow'">
          <div class="modal-container__body">
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>
                  {{ modalInfo.meeting_ref ? modalInfo.meeting_ref.topic : 'None' }}
                </h4>
              </div>
            </div>
            <section class="note-section" v-if="modalInfo.meeting_ref">
              <p class="note-section__title">
                Meeting ID:
                {{ modalInfo.meeting_ref.meeting_id ? modalInfo.meeting_ref.meeting_id : 'N/A' }}
              </p>
              <p class="note-section__date">
                Start Time:
                {{
                  modalInfo.meeting_ref.start_time
                    ? `${weekDay(modalInfo.meeting_ref.start_time)} ${formatDateTime(
                        modalInfo.meeting_ref.start_time,
                      )} at ${getTime(modalInfo.meeting_ref.start_time)}`
                    : 'None'
                }}
              </p>
              <!-- <br /> -->
              <p class="note-section__date" style="margin-top: -10px">
                End Time: <span style="color: white">{{ ' . ' }}</span>
                {{
                  modalInfo.meeting_ref.end_time
                    ? `${weekDay(modalInfo.meeting_ref.end_time)} ${formatDateTime(
                        modalInfo.meeting_ref.end_time,
                      )} at ${getTime(modalInfo.meeting_ref.end_time)}`
                    : 'None'
                }}
              </p>
              <div>
                <div>
                  <span class="">Meeting UUID: </span
                  >{{
                    modalInfo.meeting_ref.meeting_uuid ? modalInfo.meeting_ref.meeting_uuid : 'None'
                  }}
                  | <span class="">Account ID: </span
                  >{{
                    modalInfo.meeting_ref.account_id ? modalInfo.meeting_ref.account_id : 'None'
                  }}
                  |
                </div>
                <div>
                  <span class="">Host ID: </span
                  >{{ modalInfo.meeting_ref.host_id ? modalInfo.meeting_ref.host_id : 'None' }} |
                  <span class="">Operator ID: </span
                  >{{
                    modalInfo.meeting_ref.operator_id ? modalInfo.meeting_ref.operator_id : 'None'
                  }}
                  |
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Status: </span
                  >{{ modalInfo.meeting_ref.status ? modalInfo.meeting_ref.status : 'None' }} |
                  <span class="">Timezone: </span
                  >{{ modalInfo.meeting_ref.timezone ? modalInfo.meeting_ref.timezone : 'None' }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Start URL: </span
                  >{{ modalInfo.meeting_ref.start_url ? modalInfo.meeting_ref.start_url : 'None' }}
                </div>
                <div>
                  <span class="">Duration: </span
                  >{{ modalInfo.meeting_ref.duration ? modalInfo.meeting_ref.duration : 'None' }} |
                  <span class="">Original Duration: </span
                  >{{
                    modalInfo.meeting_ref.original_duration
                      ? modalInfo.meeting_ref.original_duration
                      : 'None'
                  }}
                  |
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Total Minutes: </span
                  >{{
                    modalInfo.meeting_ref.total_minutes
                      ? modalInfo.meeting_ref.total_minutes
                      : 'None'
                  }}
                  | <span class="">Recurrence: </span
                  >{{
                    modalInfo.meeting_ref.recurrence ? modalInfo.meeting_ref.recurrence : 'None'
                  }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Join URL: </span
                  >{{ modalInfo.meeting_ref.join_url ? modalInfo.meeting_ref.join_url : 'None' }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Operator: </span
                  >{{ modalInfo.meeting_ref.operator ? modalInfo.meeting_ref.operator : 'None' }} |
                  <span class="">Operation: </span
                  >{{ modalInfo.meeting_ref.operation ? modalInfo.meeting_ref.operation : 'None' }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Participants: </span>
                  <div
                    v-for="(participant, i) in modalInfo.meeting_ref.participants"
                    :key="i"
                    style="margin-left: 0.5rem"
                  >
                    {{ i + 1 }}:
                    <div
                      v-for="(value, propertyName) in participant"
                      :key="propertyName"
                      style="margin-left: 1rem"
                    >
                      <div v-if="propertyName === 'secondary_data'">
                        {{ propertyName }}:
                        <div
                          v-for="(data, secondaryName) in value"
                          :key="secondaryName"
                          style="margin-left: 1.5rem"
                        >
                          {{ secondaryName }}: {{ `${data}` }}
                        </div>
                      </div>
                      <div v-else>{{ propertyName }}: {{ `${value}` }}</div>
                    </div>
                  </div>
                  <!-- {{
                    modalInfo.meeting_ref.participants ? modalInfo.meeting_ref.participants : 'None'
                  }} -->
                </div>
                <div>
                  <span class="">Type: </span
                  >{{ modalInfo.meeting_ref.type ? modalInfo.meeting_ref.type : 'None' }} |
                  <span class="">Zoom Account: </span
                  >{{
                    modalInfo.meeting_ref.zoom_account ? modalInfo.meeting_ref.zoom_account : 'None'
                  }}
                </div>
              </div>
            </section>
            <section v-else>
              <p>No Info to Display</p>
            </section>
          </div>
        </div>
        <div v-else-if="modalName === 'alert'">
          <div class="modal-container__body">
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>
                  {{ modalInfo.title ? modalInfo.title : 'None' }}
                </h4>
              </div>
            </div>
            <section class="note-section" v-if="modalInfo">
              <p class="note-section__title">
                Alert ID:
                {{ modalInfo.id ? modalInfo.id : 'N/A' }}
              </p>
              <!-- <p class="note-section__date">
                User:
                {{ modalInfo.user ? getUserName(modalInfo.user) : 'N/A' }}
              </p> -->
              <p class="note-section__date" style="margin-top: -10px">
                Is Active:
                {{ modalInfo.is_active ? modalInfo.is_active : 'N/A' }}
              </p>
              <div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">User: </span
                  >{{ modalInfo.user ? getUserName(modalInfo.user) : 'N/A' }} |
                  <span class="">Alert Level: </span
                  >{{ modalInfo.alert_level ? modalInfo.alert_level : 'N/A' }} |
                  <span class="">Resource Type: </span
                  >{{ modalInfo.resource_type ? modalInfo.resource_type : 'None' }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Configs: </span>
                  <div
                    v-for="(config, i) in modalInfo.configs_ref"
                    :key="i"
                    style="margin-left: 0.5rem"
                  >
                    {{ i + 1 }}:
                    <div style="margin-left: 1rem">
                      <div>ID: {{ config.id }}</div>
                      <div>Recurrence Frequency: {{ config.recurrence_frequency }}</div>
                      <div>Recurrence Day: {{ weekdays[config.recurrence_day] }}</div>
                      <div>Recurrence Days: {{ getWeekdays(config.recurrence_days) }}</div>
                      <div>Recipients: {{ config.recipients }}</div>
                      <div>Recipient Type: {{ config.recipient_type }}</div>
                      <div>Template: {{ config.template }}</div>
                      <div>Alert Targets: {{ config.alert_targets }}</div>
                    </div>
                  </div>
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Groups: </span>
                  <div
                    v-for="(group, i) in modalInfo.groups_ref"
                    :key="i"
                    style="margin-left: 0.5rem; margin-bottom: 1rem"
                  >
                    <div>Order: {{ group.group_order }}</div>
                    <div>Condition: {{ group.group_condition }}</div>
                    <div
                      v-for="(operand, i) in group.operands_ref"
                      :key="i"
                      style="margin-left: 1rem"
                    >
                      {{ operand.operand_order }} - {{ operand.operand_identifier }}
                      {{ operand.operand_operator }} {{ operand.operand_value }} ({{
                        operand.data_type
                      }}) {{ operand.operand_condition }}
                    </div>
                  </div>
                </div>
              </div>
            </section>
            <section v-else>
              <p>No Info to Display</p>
            </section>
          </div>
        </div>
        <div v-else-if="modalName === 'user'">
          <div class="modal-container__body">
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>{{ modalInfo.first_name }} {{ modalInfo.last_name }}</h4>
              </div>
            </div>
            <section class="note-section">
              <p class="note-section__title">General Info</p>
              <div>
                <div>
                  <span class="">Email:</span>
                  {{ modalInfo.email ? modalInfo.email : 'None' }} |
                  <span class="">Is Active:</span> {{ modalInfo.is_active }} |
                  <span class="">Is Invited:</span> {{ modalInfo.is_invited }} |
                </div>
                <div>
                  <span class="">Is Admin:</span> {{ modalInfo.is_admin }} |
                  <span class="">Is Staff:</span> {{ modalInfo.is_staff }} |
                  <span class="">User Level:</span> {{ modalInfo.user_level }} |
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Role:</span> {{ modalInfo.role }} |
                  <span class="">Timezone:</span> {{ modalInfo.timezone }}
                </div>
                <div>
                  <span class="">Activated Managr Configs:</span>
                  {{
                    modalInfo.activated_managr_configs ? modalInfo.activated_managr_configs : 'None'
                  }}
                </div>
              </div>
            </section>
            <section class="note-section">
              <p class="note-section__title">User Slack Integrations</p>
              <div>
                <div>
                  <span class="">Slack ID:</span>
                  {{ modalInfo.slack_ref ? modalInfo.slack_ref.slack_id : 'None' }} |
                  <span class="">Channel:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.channel
                      ? modalInfo.slack_account.channel
                      : 'None'
                  }}
                  |
                </div>
                <div>
                  <span class="">Organization Slack:</span>
                  {{ modalInfo.organization_ref.slack_integration }} |
                  <span class="">Is Onboarded:</span> {{ modalInfo.onboarding }} |
                </div>
                <div>
                  <span class="">Recap Channel:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.recap_channel
                      ? modalInfo.slack_account.recap_channel
                      : 'None'
                  }}
                  |
                  <span class="">Recap Recievers:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.recap_receivers
                      ? modalInfo.slack_account.recap_receivers
                      : 'None'
                  }}
                </div>
              </div>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Salesforce ({{
                  modalInfo.salesforce_account_ref ? modalInfo.salesforce_account_ref.id : 'None'
                }})
              </p>
              <div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">SFDC ID:</span>
                  {{
                    modalInfo.salesforce_account_ref &&
                    modalInfo.salesforce_account_ref.salesforce_id
                      ? modalInfo.salesforce_account_ref.salesforce_id
                      : 'None'
                  }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">sobjects:</span>
                  {{
                    modalInfo.salesforce_account_ref && modalInfo.salesforce_account_ref.sobjects
                      ? modalInfo.salesforce_account_ref.sobjects
                      : 'None'
                  }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Instance URL:</span>
                  {{
                    modalInfo.salesforce_account_ref &&
                    modalInfo.salesforce_account_ref.instance_url
                      ? modalInfo.salesforce_account_ref.instance_url
                      : 'None'
                  }}
                </div>
                <div>
                  <span class="">Access Token:</span>
                  {{
                    modalInfo.salesforce_account_ref &&
                    modalInfo.salesforce_account_ref.access_token
                      ? modalInfo.salesforce_account_ref.access_token
                      : 'None'
                  }}
                </div>
              </div>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Nylas ({{ modalInfo.nylas_ref ? modalInfo.nylas_ref.id : 'None' }})
              </p>
              <div>
                <div>
                  <span class="">Access Token:</span>
                  {{
                    modalInfo.nylas_ref && modalInfo.nylas_ref.access_token
                      ? modalInfo.nylas_ref.access_token
                      : 'None'
                  }}
                  |
                  <span class="">Email:</span>
                  {{
                    modalInfo.nylas_ref && modalInfo.nylas_ref.email_address
                      ? modalInfo.nylas_ref.email_address
                      : 'None'
                  }}
                  |
                </div>
                <div>
                  <span class="">Event Calendar ID:</span>
                  {{
                    modalInfo.nylas_ref && modalInfo.nylas_ref.event_calendar_id
                      ? modalInfo.nylas_ref.event_calendar_id
                      : 'None'
                  }}
                  |
                  <span class="">Provider:</span>
                  {{
                    modalInfo.nylas_ref && modalInfo.nylas_ref.provider
                      ? modalInfo.nylas_ref.provider
                      : 'None'
                  }}
                </div>
              </div>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Zoom ({{ modalInfo.zoom_ref ? modalInfo.zoom_ref.id : 'None' }})
              </p>
              <div style="margin-bottom: 0.5rem">
                <div style="margin-bottom: 0.5rem">
                  <span class="">Zoom ID:</span>
                  {{
                    modalInfo.zoom_ref && modalInfo.zoom_ref.zoom_id
                      ? modalInfo.zoom_ref.zoom_id
                      : 'None'
                  }}
                  |
                  <span class="">Timezone:</span>
                  {{
                    modalInfo.zoom_ref && modalInfo.zoom_ref.timezone
                      ? modalInfo.zoom_ref.timezone
                      : 'None'
                  }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Account ID:</span>
                  {{
                    modalInfo.zoom_ref && modalInfo.zoom_ref.account_id
                      ? modalInfo.zoom_ref.account_id
                      : 'None'
                  }}
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Access Token:</span>
                  {{
                    modalInfo.zoom_ref && modalInfo.zoom_ref.access_token
                      ? modalInfo.zoom_ref.access_token
                      : 'None'
                  }}
                </div>
                <div>
                  <span class="">Fake Meeting ID:</span>
                  {{
                    modalInfo.zoom_ref && modalInfo.zoom_ref.fake_meeting_id_ref
                      ? modalInfo.zoom_ref.fake_meeting_id_ref
                      : 'None'
                  }}
                </div>
              </div>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Slack Account ({{
                  modalInfo.slack_account ? modalInfo.slack_account.slack_id : 'None'
                }})
              </p>
              <div>
                <div>
                  <span class="">Slack ID:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.slack_id
                      ? modalInfo.slack_account.slack_id
                      : 'None'
                  }}
                  |
                  <span class="">Channel:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.channel
                      ? modalInfo.slack_account.channel
                      : 'None'
                  }}
                  |
                </div>
                <div style="margin-bottom: 0.5rem">
                  <span class="">Zoom Channel:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.zoom_channel
                      ? modalInfo.slack_account.zoom_channel
                      : 'None'
                  }}
                  |
                  <span class="">Recap Receivers:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.recap_receivers
                      ? modalInfo.slack_account.recap_receivers
                      : 'None'
                  }}
                </div>
                <div>
                  <span class="">Real Time Alert Configs:</span>
                  {{
                    modalInfo.slack_account && modalInfo.slack_account.realtime_alert_configs
                      ? modalInfo.slack_account.realtime_alert_configs
                      : 'None'
                  }}
                </div>
              </div>
            </section>
          </div>
        </div>
        <div v-else-if="modalName === 'usersOverview'">
          <div class="modal-container__body">
            <div
              class="flex-row-spread sticky border-bottom"
              style="margin-bottom: 1rem; background-color: white; z-index: 3"
            >
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>{{ this.selected_org.name }}'s Users</h4>
              </div>
            </div>
            <div class="invite-list-users__section__container" style="margin-bottom: 1rem">
              <div class="invite-list-users__section__item underline">
                Total: {{ modalInfo.length }}
              </div>
              <div class="invite-list-users__section__item underline">
                Invited: {{ invitedUsers ? invitedUsers.length : 0 }}
              </div>
              <div class="invite-list-users__section__item underline">
                Active: {{ activeUsers ? activeUsers.length : 0 }}
              </div>
              <div class="invite-list-users__section__item"></div>
            </div>
            <div
              v-for="member in modalInfo"
              :key="member.id"
              class="invite-list-users__section__container"
            >
              <template v-if="member">
                <div
                  style="display: flex; align-items: flex-start; font-size: 14px"
                  class="invite-list-users__section__item col"
                >
                  <!-- {{member.is_active ? member.first_name : 'Pending'}} -->
                  {{
                    !member.first_name
                      ? 'Pending'
                      : member.is_active
                      ? member.first_name
                      : member.first_name
                  }}
                  <p style="color: #beb5cc; font-size: 0.65rem; margin-top: 0.25rem">
                    {{
                      !member.first_name
                        ? member.email
                        : member.is_active
                        ? member.email
                        : member.email
                    }}
                  </p>
                </div>
                <div
                  v-if="member.user_level == 'MANAGER'"
                  style="display: flex; align-items: flex-start; font-size: 14px"
                  class="invite-list-users__section__item"
                >
                  Manager
                </div>
                <div
                  v-else-if="member.user_level == 'SDR'"
                  style="display: flex; align-items: flex-start; font-size: 14px"
                  class="invite-list-users__section__item"
                >
                  SDR
                </div>
                <div
                  v-else-if="member.user_level == 'REP'"
                  style="display: flex; align-items: flex-start; font-size: 14px"
                  class="invite-list-users__section__item"
                >
                  REP
                </div>
                <div
                  style="display: flex; align-items: flex-start; font-size: 14px"
                  class="invite-list-users__section__item"
                >
                  <!-- {{ member.is_active ? 'Registered' : 'Pending...' }} -->
                  {{
                    !member.first_name
                      ? 'Pending...'
                      : member.is_active
                      ? 'Registered'
                      : 'Deactivated'
                  }}
                </div>
                <div
                  style="display: flex; align-items: flex-start"
                  class="invite-list-users__section__item invite-list-users__status"
                >
                  <span :class="member.slack_ref ? '' : 'grayscale'">
                    <img src="@/assets/images/slackLogo.png" height="18px" alt="" />
                  </span>
                  <span
                    v-if="member.crm === 'SALESFORCE'"
                    :class="member.has_salesforce_integration ? '' : 'grayscale'"
                  >
                    <img src="@/assets/images/salesforce.png" height="18px" alt="" />
                  </span>
                  <span
                    v-else-if="member.crm === 'HUBSPOT'"
                    :class="member.has_hubspot_integration ? '' : 'grayscale'"
                  >
                    <img src="@/assets/images/hubspot-single-logo.svg" height="18px" alt="" />
                  </span>
                  <span v-else :class="'grayscale'">
                    <img src="@/assets/images/revoke.svg" style="margin-right: 20px; margin-left: 2px" height="18px" alt="" />
                  </span>
                  <span :class="member.has_zoom_integration ? '' : 'grayscale'">
                    <img src="@/assets/images/zoom.png" alt="" height="18px" />
                  </span>
                  <span :class="member.nylas_ref ? '' : 'grayscale'">
                    <img src="@/assets/images/gmailCal.png" alt="" height="18px" />
                  </span>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
      <div v-else>No Modal Info</div>
    </Modal>
    <Modal
      v-if="displayCommandModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetCommandsEdit()
        }
      "
    >
      <div class="modal-container" v-if="contentModalInfo">
        <div v-if="contentType === 'PullUsageData'">
          <div class="flex-row-spread sticky border-bottom">
            <div class="flex-row">
              <img src="@/assets/images/logo.png" class="logo" alt="" />
              <h4>Pull Usage Data</h4>
            </div>
            <div>
              <!-- <button
                class="green_button sized copy-margin"
                v-clipboard:copy="formatCopyObject(contentModalInfo)"
                v-clipboard:success="onCopy"
                v-clipboard:error="onError"
              >
                Copy All
              </button> -->
            </div>
          </div>
          <section class="note-section" v-for="(content, i) in contentModalInfo" :key="i">
            <div style="display: flex; justify-content: space-between">
              <p class="note-section__title">
                {{ content.date ? `${getMonth(content.date)}, ${getYear(content.date)}` : 'N/A' }}
              </p>
              <button
                class="green_button sized"
                v-clipboard:copy="formatCopyObject(content)"
                v-clipboard:success="onCopy"
                v-clipboard:error="onError"
              >
                <!-- <img src="@/assets/images/copy.svg" class="invert" style="height: 1.25rem" alt="" /> -->
                Copy
              </button>
            </div>
            <div>
              <div style="margin-bottom: 0.5rem">
                <span class="">Users:</span>
                {{ content.total && content.total.users !== null ? content.total.users : 'None' }} |
                <span class="">Workflows:</span>
                {{
                  content.total && content.total.workflows !== null
                    ? content.total.workflows
                    : 'None'
                }}
              </div>
              <div>
                <span class="">Accounts Created:</span>
                {{
                  content.total && content.total.creates.accounts !== null
                    ? content.total.creates.accounts
                    : 'None'
                }}
                | <span class="">Contacts Created:</span>
                {{
                  content.total && content.total.creates.contacts !== null
                    ? content.total.creates.contacts
                    : 'None'
                }}
                |
              </div>
              <div style="margin-bottom: 0.5rem">
                <span class="">Opportunities Created:</span>
                {{
                  content.total && content.total.creates.opportunities !== null
                    ? content.total.creates.opportunities
                    : 'null'
                }}
                | <span class="">Products Created:</span>
                {{
                  content.total && content.total.creates.products !== null
                    ? content.total.creates.products
                    : 'None'
                }}
                | <span class="">Total Created:</span>
                {{
                  content.total && content.total.creates.total !== null
                    ? content.total.creates.total
                    : 'None'
                }}
              </div>
              <div>
                <span class="">Alert Updates:</span>
                {{
                  content.total && content.total.updates && content.total.updates.alert !== null
                    ? content.total.updates.alert
                    : 'None'
                }}
                | <span class="">Command Updates:</span>
                {{
                  content.total && content.total.updates.command !== null
                    ? content.total.updates.command
                    : 'None'
                }}
                |
              </div>
              <div style="margin-bottom: 0.5rem">
                <span class="">Meeting Updates:</span>
                {{
                  content.total && content.total.updates.meeting !== null
                    ? content.total.updates.meeting
                    : 'None'
                }}
                | <span class="">Pipeline Updates:</span>
                {{
                  content.total && content.total.updates.pipeline !== null
                    ? content.total.updates.pipeline
                    : 'None'
                }}
                | <span class="">Total Updates:</span>
                {{
                  content.total && content.total.updates.total !== null
                    ? content.total.updates.total
                    : 'None'
                }}
              </div>
            </div>
            <h2 class="note-section__small_title">Per Organization:</h2>
            <div v-for="(orgItem, j) in content.orgs" :key="`item${j}`">
              <div>Name: {{ orgItem.name }}</div>
              <div>
                Org: Avg Updates per Session: {{ Number(orgItem['session average']).toFixed(2) }} |
                Avg Total Sessions: {{ orgItem['average total sessions'] }} | Updates:
                {{ orgItem['updates'] }} | Creates: {{ orgItem['creates'] }}
              </div>
              <div>
                <h4 style="margin-top: 1rem; margin-bottom: 0.25rem">Users:</h4>
                <div v-for="(user, k) in orgItem.users" :key="`users${k}`">
                  <div>
                    {{ user.userName }} - Avg Updates per Session:
                    {{ Number(user['session average']).toFixed(2) }} | Total Sessions:
                    {{ user['total sessions'] }} | Updates: {{ user['updates'] }} | Creates:
                    {{ user['creates'] }}
                  </div>
                </div>
              </div>
              <div class="separator"></div>
            </div>
          </section>
        </div>
      </div>
      <div v-else>No Modal Info</div>
    </Modal>
    <!-- Create Team -->
    <Modal
      v-if="newTeam"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleCancel()
        }
      "
    >
      <form v-if="true /*hasSlack*/" class="invite-form modal-form" style="margin-top: 7.5rem">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Create a Team</h3>
          </div>
          <!-- <div class="flex-row">
            <img
              @click="handleCancel"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="filter: invert(30%); cursor: pointer"
            />
          </div> -->
        </div>

        <div
          style="
            display: flex;
            justify-content: center;
            flex-direction: column;
            margin-top: -3rem;
            margin-bottom: 1rem;
          "
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <input
                  placeholder="Team Name"
                  v-model="teamName"
                  style="width: 33vw"
                  class="template-input modal-input"
                  type="text"
                  name=""
                  id=""
                  :disabled="false /*savingTemplate*/"
                />
              </template>
            </FormField>
          </div>
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Team Lead"
                  v-model="teamLead"
                  :options="
                    team.filter((u) => u.id !== user.id)
                  "
                  openDirection="below"
                  style="width: 33vw"
                  selectLabel="Enter"
                  label="email"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Team Lead
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="createTeamSubmit"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 1.75rem"
                text="Save"
                :loading="pulseLoading"
                >Save</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <!-- Edit Team -->
    <Modal
      v-if="editTeam"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleCancel()
        }
      "
    >
      <form v-if="true /*hasSlack*/" class="invite-form modal-form" style="margin-top: 7.5rem">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 @click="test(selectedUsers)" class="invite-form__title">Add Members to Team</h3>
          </div>
        </div>

        <div
          style="display: flex; justify-content: center; flex-direction: column; margin-top: -3rem"
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <!-- Make this one Team -->
                <Multiselect
                  placeholder="Select Team"
                  v-model="selectedTeam"
                  :options="teamList"
                  openDirection="below"
                  style="width: 33vw"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Team
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
          <!-- <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Users"
                  v-model="selectedUsers"
                  :options="orgUsers.filter(u => !u.is_admin)"
                  openDirection="below"
                  style="width: 33vw; margin-bottom: 1rem;"
                  selectLabel="Enter"
                  label="email"
                  :multiple="true"
                >
                  <template slot="noResult">
                    <p class="multi-slot">Please select a team.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Users
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div> -->
        </div>
        <div class="invite-form__actions">
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="editTeamSubmit"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Save"
                :loading="pulseLoading"
                >Save</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <!-- Change Team Lead -->
    <Modal
      v-if="changeTeamLead"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleCancel()
        }
      "
    >
      <form v-if="true /*hasSlack*/" class="invite-form modal-form" style="margin-top: 7.5rem">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Change Team Lead</h3>
          </div>
        </div>

        <div
          style="display: flex; justify-content: center; flex-direction: column; margin-top: -3rem"
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Users"
                  v-model="selectedTeamLead"
                  :options="selectedTeamUsers"
                  openDirection="below"
                  style="width: 33vw; margin-bottom: 1rem;"
                  selectLabel="Enter"
                  label="email"
                  :multiple="false"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No Results</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select User
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="changeTeamLeader"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Save"
                :loading="pulseLoading"
                >Save</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <div class="flex-row" style="justify-content: space-between; width: 82vw; margin-left: 2rem;">
      <div class="flex-row">
        <small class="pipeline-header">Quick Commands:</small>
        <button
          @click.stop="
            showCommandList = !showCommandList
            showOrgList = false
          "
          class="text-button"
          style="cursor: pointer"
        >
          Commands
          <img height="12px" src="@/assets/images/downArrow.svg" alt="" />
        </button>
        <div v-outside-click="closeListSelect" v-show="showCommandList" class="list-section">
          <div class="list-section__title flex-row-spread">
            <p>Commands</p>
          </div>
          <button
            @click="selectCommand(command)"
            :v-model="selectedCommand"
            class="list-button"
            v-for="command in commandOptions"
            :key="command.id"
          >
            {{ command.label }}
          </button>
        </div>
        <small class="pipeline-header">Organization:</small>
        <button
          @click.stop="
            showOrgList = !showOrgList
            showCommandList = false
          "
          class="text-button"
          style="cursor: pointer"
        >
          Organization
          <img height="12px" src="@/assets/images/downArrow.svg" alt="" />
        </button>
        <small class="pipeline-header">Search Orgs: </small>
        <div class="search-bar">
          <img src="@/assets/images/search.svg" style="height: 18px" alt="" />
          <input
            type="search"
            placeholder="search"
            v-model="filterText"
            @input="showOrgList = true"
          />
        </div>
        <div
          v-outside-click="closeListSelect"
          v-show="showOrgList"
          class="list-section"
          style="left: 310px"
        >
          <div class="list-section__title flex-row-spread">
            <p>Organizations</p>
          </div>
          <button
            @click="selectOrg(org)"
            :v-model="selected_org"
            class="list-button"
            v-for="org in filteredOrganizations"
            :key="org.id"
          >
            {{ org.name }}
          </button>
        </div>
        <div v-for="(filter, i) in activeFilters" :key="i" class="main">
          <strong style="font-size: 14px">{{ filter }}</strong>
          <small style="font-weight: 400px; margin-left: 0.2rem">{{ setFilters[i][0] }}</small>
          <small style="margin-left: 0.2rem">{{ setFilters[i][1] }}</small>
        </div>
  
        <section style="position: relative">
          <div style="display: flex">
            <button
              v-if="activeFilters.length < 4 && selected_org"
              @click.stop="addingFilter"
              class="add-filter-button"
            >
              <img
                src="@/assets/images/filter.svg"
                class="invert"
                height="12px"
                style="margin-right: 0.25rem"
                alt=""
              />Filter
            </button>
            <button
              v-if="activeFilters.length && selected_org"
              @click.stop="resetFilters"
              class="add-filter-button"
            >
              <img
                src="@/assets/images/filter.svg"
                class="invert"
                height="12px"
                style="margin-right: 0.25rem"
                alt=""
              />Clear
            </button>
          </div>
          <div v-outside-click="closeFilters" v-if="filtering">
            <div v-if="filtering" class="filter-selection">
              <div class="filter-selection__body">
                <Multiselect
                  placeholder="Team/User"
                  @select="resetFilters"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem; z-index: 4"
                  v-model="selectedTeamOrUser"
                  :options="teamOrUser"
                  openDirection="below"
                  selectLabel="Enter"
                  track-by="name"
                  label="name"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
              </div>
              <div class="filter-selection__body">
                <Multiselect
                  placeholder="Filter"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem; z-index: 3"
                  @select="applyFilter($event)"
                  v-model="selectedFilter"
                  :options="
                    selectedTeamOrUser
                      ? selectedTeamOrUser.name === 'team'
                        ? teamList
                        : orgUsers
                      : []
                  "
                  openDirection="below"
                  selectLabel="Enter"
                  track-by="name"
                  :customLabel="filtersLabel"
                  :label="
                    selectedTeamOrUser ? (selectedTeamOrUser.name === 'team' ? 'name' : 'email') : ''
                  "
                >
                  <template slot="placeholder">
                    <p class="multi-slot">
                      {{ selectedTeamOrUser ? `Filters` : `Please select User/Team.` }}
                    </p>
                  </template>
                </Multiselect>
              </div>
            </div>
          </div>
        </section>
      </div>
      <div>
        <h4 v-if="selected_org" @click="selected_org = null" style="cursor: pointer; padding-top: 0.25rem; margin: 0; font-size: 14px; justify-self: flex-end;">
          <img
            style="margin-right: 0px; filter: invert(40%); height: 0.6rem;"
            src="@/assets/images/left.svg"
            height="13px"
          />
          Back
        </h4>
      </div>
    </div>
    <div class="staff__main_page">
      <template v-if="selected_org && selected_org.id && page !== 'TeamManager'">
        <div v-if="loading">Loading</div>
        <template v-else>
          <!-- <div style="border-bottom: 1px solid black; margin-left: 1rem"> -->
          <!-- Top Section -->
          <div class="invite-list__container" style="margin-top: 1rem;">
            <!-- <img class="back-logo" style="right: 18%; bottom: 57%" src="@/assets/images/logo.png" /> -->
            <!-- <h4 @click="selected_org = null" style="cursor: pointer; padding-top: 0.25rem; margin: 0;">
              <img
                style="margin-right: 4px; filter: invert(40%);"
                src="@/assets/images/left.svg"
                height="13px"
              />
              Back
            </h4> -->
            <div style="display: flex; flex-direction: column; margin-left: 1.2rem;">
              <h2 class="org-title">{{ selected_org.name }}</h2>
              <h4 class="org-subtitle">
                {{ selected_org.days_since_created_ref }} days active
              </h4>
            </div>
            <div style="display: flex; margin-left: 1.2rem; width: 75vw; justify-content: space-between;">
              <div class="left-actions">
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">State:</div>
                  </div>
                  <div>
                    <Multiselect
                      placeholder="State"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem; z-index: 3"
                      v-model="stateActive"
                      :options="states"
                      openDirection="below"
                      selectLabel="Enter"
                      track-by="id"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">Admin:</div>
                  </div>
                  <Multiselect
                    v-model="newAdmin"
                    @select="handleConfirm"
                    :options="orgUsers.filter(user => !user.is_admin) /* do not show the current admin */"
                    openDirection="below"
                    style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem;"
                    selectLabel="Enter"
                    label="email"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <!-- <img src="@/assets/images/search.svg" alt="" /> -->
                        {{`${admin ? admin.email : ''}`}}
                      </p>
                    </template>
                  </Multiselect>
                </div>
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">Ignore Emails:</div>
                  </div>
                  <div class="" style="width: 48%">
                    <input
                      class="wide gray-border"
                      style="border: 1px solid #e8e8e8; padding: 0.5rem;"
                      type="search"
                      v-model="ignoreEmails"
                      placeholder="None"
                    />
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">Has Products:</div>
                  </div>
                  <div>
                    <Multiselect
                      v-model="hasProducts"
                      :options="[{label: 'Yes', value: true}, {label: 'No', value: false}]"
                      openDirection="below"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem;"
                      selectLabel="Enter"
                      label="label"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <!-- <img src="@/assets/images/search.svg" alt="" /> -->
                          {{`${hasProducts.label}`}}
                        </p>
                      </template>
                    </Multiselect>
                    <!-- <input type="checkbox" v-model="hasProducts" /> -->
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <button
                    style="margin: 1rem 0 0 0; align-self: center"
                    class="invite_button"
                    @click="postOrgUpdates()"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
              <div class="right-actions">
                <div class="invite-list__section__container">
                  <div style="display: flex; flex-direction: column; margin-left: 1rem;">
                    <p style="margin: 0">
                      Users:
                      <span v-if="filteredOrgUsers" class="green">{{ filteredOrgUsers.length }}</span>
                    </p>
                    <Multiselect
                      placeholder="Select User"
                      @select="openModal('user', $event)"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 0.5rem;"
                      v-model="selectedUser"
                      :options="filteredOrgUsers"
                      openDirection="below"
                      selectLabel="Enter"
                      track-by="id"
                      :custom-label="customUserLabel"
                      :multiple="false"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <div style="display: flex; flex-direction: column; margin-left: 1rem; margin-top: 3rem;">
                    <p style="margin: 0;">
                      Select Action:
                    </p>
                    <Multiselect
                      placeholder="Select Action"
                      @select="selectAction($event)"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 0.5rem;"
                      v-model="selectedAction"
                      :options="actionOptions"
                      openDirection="below"
                      selectLabel="Enter"
                      track-by="label"
                      label="label"
                      :multiple="false"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- Team Section -->
          <div class="invite-list__container" style="margin-top: 1rem;">
            <!-- <img class="back-logo" style="right: 18%; bottom: 57%" src="@/assets/images/logo.png" /> -->
            <!-- <h4 @click="selected_org = null" style="cursor: pointer; padding-top: 0.25rem; margin: 0;">
              <img
                style="margin-right: 4px; filter: invert(40%);"
                src="@/assets/images/left.svg"
                height="13px"
              />
              Back
            </h4> -->
            <div class="team-top-container">
              <div>
                <div style="margin-bottom: 1rem; margin-left: 0.5rem">Teams: <span class="green">{{ teamList.length }}</span></div>
                <div>
                  <Multiselect
                    placeholder="Select Team"
                    v-model="selectedViewedTeam"
                    :options="teamList"
                    openDirection="below"
                    style="width: 20vw; z-index: 3; margin-left: 0.5rem"
                    selectLabel="Enter"
                    track-by="id"
                    label="name"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results. Try loading more</p>
                    </template>
                    <template slot="afterList">
                      <!-- <p class="multi-slot__more" @click="listUsers(slackMembers.nextCursor)">
                        Load More
                        <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                      </p> -->
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        Select Team
                      </p>
                    </template>
                  </Multiselect>
                </div>
              </div>
              <div>
                <button class="green_button" type="submit" @click="handleNewTeam">
                  Create Team
                </button>
              </div>
            </div>
            <div class="">
              <section v-if="manageTeamSelected">
                <Invite
                  class="invite-users__inviter"
                  :handleEdit="handleEdit"
                  :inviteOpen="inviteOpen"
                  :selectedTeamUsers="selectedTeamUsers"
                  :inviteActions="inviteActions"
                  @cancel="handleCancel"
                  @handleRefresh="() => inviteOpen = false"
                />
              </section>
            </div>
            <!-- <div style="display: flex; margin-left: 1.2rem; width: 75vw; justify-content: space-between;">
              <div class="left-actions">
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">State:</div>
                  </div>
                  <div>
                    <Multiselect
                      placeholder="State"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem; z-index: 3"
                      v-model="stateActive"
                      :options="states"
                      openDirection="below"
                      selectLabel="Enter"
                      track-by="id"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">Admin:</div>
                  </div>
                  <Multiselect
                    v-model="newAdmin"
                    @select="handleConfirm"
                    :options="orgUsers.filter(user => !user.is_admin) /* do not show the current admin */"
                    openDirection="below"
                    style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem; z-index: 5;"
                    selectLabel="Enter"
                    label="email"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        {{`${admin ? admin.email : ''}`}}
                      </p>
                    </template>
                  </Multiselect>
                </div>
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">Ignore Emails:</div>
                  </div>
                  <div class="z-more" style="width: 48%">
                    <input
                      class="wide gray-border z-more"
                      style="border: 1px solid #e8e8e8; padding: 0.5rem;"
                      type="search"
                      v-model="ignoreEmails"
                      placeholder="None"
                    />
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <div class="line-up">
                    <div class="invite-list__section__item">Has Products:</div>
                  </div>
                  <div>
                    <Multiselect
                      v-model="hasProducts"
                      :options="[{label: 'Yes', value: true}, {label: 'No', value: false}]"
                      openDirection="below"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem; z-index: 5;"
                      selectLabel="Enter"
                      label="label"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          {{`${hasProducts.label}`}}
                        </p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <button
                    style="margin: 1rem 0 0 0; align-self: center"
                    class="green_button"
                    @click="postOrgUpdates()"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
              <div class="right-actions">
                <div class="invite-list__section__container">
                  <div style="display: flex; flex-direction: column; margin-left: 1rem;">
                    <p style="margin: 0">
                      Users:
                      <span v-if="filteredOrgUsers" class="green">{{ filteredOrgUsers.length }}</span>
                    </p>
                    <Multiselect
                      placeholder="Select User"
                      @select="openModal('user', $event)"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 0.5rem;"
                      v-model="selectedUser"
                      :options="filteredOrgUsers"
                      openDirection="below"
                      selectLabel="Enter"
                      track-by="id"
                      :custom-label="customUserLabel"
                      :multiple="false"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
                <div class="invite-list__section__container">
                  <div style="display: flex; flex-direction: column; margin-left: 1rem; margin-top: 3rem;">
                    <p style="margin: 0;">
                      Select Action:
                    </p>
                    <Multiselect
                      placeholder="Select Action"
                      @select="selectAction($event)"
                      style="max-width: 20vw; margin-bottom: 1rem; margin-top: 0.5rem;"
                      v-model="selectedAction"
                      :options="actionOptions"
                      openDirection="below"
                      selectLabel="Enter"
                      track-by="label"
                      label="label"
                      :multiple="false"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
              </div>
            </div> -->
          </div>

          <!-- <div class="form__list">
            <div class="added-collection">
              <p class="added-collection__header">
                Users
                <span v-if="filteredOrgUsers" class="green">{{ filteredOrgUsers.length }}</span>
              </p>
              <div class="added-collection__body">
                <Multiselect
                  placeholder="Select User"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                  v-model="selectedUser"
                  :options="filteredOrgUsers"
                  openDirection="below"
                  selectLabel="Enter"
                  track-by="id"
                  :custom-label="customUserLabel"
                  :multiple="false"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
              </div>
              <div class="added-collection__body">
                <button class="green_button" @click="openModal('user', selectedUser)">Go</button>
                <button
                  class="green_button"
                  @click="openModal('usersOverview', filteredOrgUsers)"
                  style="margin-left: 1rem"
                >
                  Overview
                </button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">
                Slack Form
                <span v-if="filteredOrgSlackForms" class="green">{{
                  filteredOrgSlackForms.length
                }}</span>
              </p>
              <div class="added-collection__body">
                <Multiselect
                  placeholder="Select Slack Form"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                  v-model="selectedSlackForms"
                  :options="filteredOrgSlackForms"
                  openDirection="below"
                  selectLabel="Enter"
                  track-by="id"
                  :custom-label="slackFormLabel"
                  :multiple="false"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
              </div>
              <div class="added-collection__body">
                <button class="green_button" @click="openModal('slackForm', selectedSlackForms)">
                  Go
                </button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">
                Slack Form Instances
                <span v-if="filteredOrgSlackFormInstances" class="green">{{
                  filteredOrgSlackFormInstances.length
                }}</span>
              </p>
              <div class="added-collection__body">
                <button class="green_button" @click="goToSlackFormInstace()">Go</button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">
                Meeting Workflows
                <span v-if="filteredOrgMeetingWorkflows" class="green">{{
                  filteredOrgMeetingWorkflows.length
                }}</span>
              </p>
              <div class="added-collection__body">
                <button class="green_button" @click="goToMeetingWorkflow()">Go</button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">
                Alerts
                <span v-if="filteredOrgAlerts" class="green">{{ filteredOrgAlerts.length }}</span>
              </p>
              <div class="added-collection__body">
                <button class="green_button" @click="goToAlerts()">Go</button>
              </div>
            </div>
          </div> -->
        </template>
      </template>
      <template v-else-if="page === 'SlackForm'">
        <div>
          <!-- <CustomSlackForm
            :formType="selectedSlackForms.formType"
            :customForm="selectedSlackForms"
            :resource="selectedSlackForms.resource"
            :fromAdmin="true"
            :goBackAdmin="goBack"
          /> -->
          <button class="green_button back" @click="goBack">Back</button>
          <div class="invite-list__container">
            <Multiselect
              placeholder="Select Slack Form"
              style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
              v-model="selectedSlackForms"
              :options="filteredOrgSlackForms"
              openDirection="below"
              selectLabel="Enter"
              track-by="id"
              :custom-label="slackFormLabel"
              :multiple="false"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
            <h2>{{ selectedSlackForms.form_type }} {{ selectedSlackForms.resource }}</h2>
            <div v-for="field in selectedSlackForms.fields_ref" :key="field.field">
              <div style="margin-bottom: 1rem">
                {{ field.field_ref.label }} ({{ field.field_ref.api_name }})
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'SlackFormInstance'">
        <button class="green_button back" @click="goBack">Back</button>
        <div
          :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'"
          v-for="(slackFormInstance, i) in filteredOrgSlackFormInstances"
          :key="slackFormInstance.id"
        >
          <h5 class="click click_width" @click="openModal('slackFormInstance', slackFormInstance)">
            {{ slackFormInstance.template_ref ? slackFormInstance.template_ref.resource : '-' }}
            {{ slackFormInstance.template_ref ? slackFormInstance.template_ref.form_type : '-' }} by
            {{ getUserName(slackFormInstance.user) }}
            {{
              slackFormInstance.submission_date
                ? `at ${formatDateTime(slackFormInstance.submission_date)} from ${
                    slackFormInstance.update_source
                  }`
                : `(Not Submitted)`
            }}
          </h5>
        </div>
      </template>
      <template v-else-if="page === 'TeamManager'">
        <button class="green_button back" @click="goBackFromTeam">Back</button>
        <div class="invite-users">
          <section class="header">
            <div class="profile-info">
              <div class="profile-info__body">
                <h3 style="color: #41b883; background-color: #dcf8e9; padding: 4px; border-radius: 6px; cursor: default;">
                  {{ selected_org.name }}'s Teams
                </h3>
                <div class="options__section">
                  <div>
                    <Multiselect
                      placeholder="Select Team"
                      v-model="selectedViewedTeam"
                      :options="teamList"
                      openDirection="below"
                      style="width: 33vw; z-index: 3;"
                      selectLabel="Enter"
                      track-by="id"
                      label="name"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results. Try loading more</p>
                      </template>
                      <template slot="afterList">
                        <!-- <p class="multi-slot__more" @click="listUsers(slackMembers.nextCursor)">
                          Load More
                          <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                        </p> -->
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          Select Team
                        </p>
                      </template>
                    </Multiselect>
                  </div>
                  <button class="invite_button" type="submit" @click="handleNewTeam">
                    Create New Team
                  </button>
                  <button class="invite_button" type="submit" @click="handleEdit">
                    Change User's Team
                  </button>
                  <button class="invite_button" type="submit" @click="handleChangeTeamLead">
                    Change Team Lead
                  </button>
                </div>
              </div>
            </div>
          </section>

          <div class="main-content">
            <section v-if="manageTeamSelected">
              <Invite
                class="invite-users__inviter"
                :handleEdit="handleEdit"
                :inviteOpen="inviteOpen"
                :selectedTeamUsers="selectedTeamUsers"
                @cancel="handleCancel"
                @handleRefresh="() => inviteOpen = false"
              />
            </section>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'MeetingWorkflow'">
        <button class="green_button back" @click="goBack">Back</button>
        <div
          :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'"
          v-for="(meetingWorkflow, i) in filteredOrgMeetingWorkflows"
          :key="meetingWorkflow.id"
        >
          <h4 class="click click_width" @click="openModal('meetingWorkflow', meetingWorkflow)">
            {{
              meetingWorkflow.meeting_ref
                ? `${meetingWorkflow.meeting_ref.topic}  (${meetingWorkflow.meeting_ref.start_time}) - ${meetingWorkflow.user_ref.email}`
                : 'No meeting tied to this workflow'
            }}
          </h4>
        </div>
      </template>
      <template v-else-if="page === 'OrgAlerts'">
        <button class="green_button back" @click="goBack">Back</button>
        <div
          :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'"
          v-for="(alert, i) in filteredOrgAlerts"
          :key="alert.id"
        >
          <h5 class="click click_width" @click="openModal('alert', alert)">
            {{ alert.title ? alert.title : 'N/A' }} ({{ getUserName(alert.user) }})
            <!-- ({{ alert.alert_level ? alert.alert_level : 'N/A' }}) by
            {{ getUserName(alert.user) }} -->
          </h5>
        </div>
      </template>
      <template v-else>
        <div class="" style="margin-top: 1rem;">
          <div style="display: flex; flex-direction: row; justify-content: flex-start; height: 30vh; width: 100%;">
            <div class="added-collection padding" style="width: 25vw; height: 28vh; display: flex; justify-content: flex-start; flex-direction: column; align-items: flex-start; margin-right: 1rem;;">
              <h4 style="margin-top: 1rem; margin-bottom: 1rem;">Total Users: {{trialUsers.length}}</h4>
              <h4 style="margin-top: 1rem; margin-bottom: 1rem;">Active Users: {{activeTrialUsers.length}}</h4>
              <h4 style="margin-bottom: 0rem; margin-top: 0.75rem;">Deactivate:</h4>
              <div style="display: flex; align-items: center;">
                <Multiselect
                  placeholder="Select Org to Deactivate"
                  style="max-width: 18vw; margin-bottom: 1rem; margin-top: 1rem"
                  v-model="selectedDeactivateOrg"
                  :options="filteredActiveOrganizations"
                  openDirection="below"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                  :multiple="false"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
                <button @click="deactivateOrg" class="green_button" style="height: 2rem; margin-left: 1rem;">Deactivate</button>
              </div>
            </div>
            <!-- <div class="added-collection padding" style="flex-direction: row; width: 35vw; height: 16vh; align-items: center;">
              Chart Here
            </div> -->
          </div>
          <div class="added-collection padding" style="width: 100%; justify-content: center;">
            <div class="flex-row-spread" style="width: 10rem;">
              <h4>Filter by day:</h4>
              <input type="number" min="0" v-model="filterByDay" style="width: 3.5rem; padding: 4px;" class="search-bar" />
            </div>
            <div style="height: 45vh;">
              <div class="flex-row-spread" style="margin-bottom: 0.5rem;">
                <div style="width: 35%">User</div>
                <div style="width: 25%">Integrations</div>
                <div style="width: 25%">Days Active</div>
                <div style="width: 25%">Total Updates</div>
              </div>
              <div style="overflow: scroll; height: 85%;">
                <div v-for="user in dayTrialUsers" :key="user.id" class="flex-row-spread" style="margin-bottom: 0.25rem;">
                  <div style="width: 35%">{{ user.email }}</div>
                  <div class="flex-row-spread" style="width: 25%">
                    <div
                      style="display: flex; align-items: flex-start;"
                      class="invite-list-users__section__item invite-list-users__status"
                    >
                      <span :class="user.slack_integration ? '' : 'grayscale'">
                        <img src="@/assets/images/slackLogo.png" height="18px" alt="" />
                      </span>
                      <span
                        v-if="user.crm === 'SALESFORCE'"
                        :class="user.salesforce_account ? '' : 'grayscale'"
                      >
                        <img src="@/assets/images/salesforce.png" height="18px" alt="" />
                      </span>
                      <span
                        v-else-if="user.crm === 'HUBSPOT'"
                        :class="user.hubspot_account ? '' : 'grayscale'"
                      >
                        <img src="@/assets/images/hubspot-single-logo.svg" height="18px" alt="" />
                      </span>
                      <span v-else :class="'grayscale'">
                        <img src="@/assets/images/revoke.svg" style="margin-right: 20px; margin-left: 2px" height="18px" alt="" />
                      </span>
                      <span :class="user.nylas ? '' : 'grayscale'">
                        <img src="@/assets/images/gmailCal.png" alt="" height="18px" />
                      </span>
                    </div>
                  </div>
                  <div style="width: 25%">{{user.days_active}}</div>
                  <div style="width: 25%">{{user.total_updates}}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <h2>Completed Tasks <span v-if="!showAdminTasks" @click="showAdminTasks = !showAdminTasks" style="cursor: pointer;">></span><span v-else @click="showAdminTasks = !showAdminTasks" style="cursor: pointer;">v</span></h2>
        <div v-if="showAdminTasks">
          <div v-for="(task, i) in adminTasks" :key="task.pk">
            <div
              :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'"
              @click="openModal('task', task)"
            >
              <h4 class="click click_width">
                {{ task.fields.task_name }} ({{ formatDateTime(task.fields.run_at) }},
                {{ getTime(task.fields.run_at) }})
                <span :style="task.fields.last_error ? 'color: red;' : 'color: green;'">{{
                  task.fields.last_error ? '[ERROR]' : '[SUCCESS]'
                }}</span>
              </h4>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'
import AlertTemplate from '@/services/alerts'
import { MeetingWorkflows } from '@/services/salesforce'
import Organization from '@/services/organizations'
import User from '@/services/users'
import CollectionManager from '@/services/collectionManager'
import FormField from '@/components/forms/FormField'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import Invite from '../settings/_pages/_Invite'
// import CustomSlackForm from '@/views/settings/CustomSlackForm'

export default {
  name: 'Staff',
  components: {
    // CustomSlackForm,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    FormField,
    PulseLoadingSpinnerButton,
    Invite,
  },
  data() {
    return {
      commandOptions: [
        { label: 'Salesforce Resources', value: 'SALESFORCE_RESOURCES' },
        { label: 'Salesforce Fields', value: 'SALESFORCE_FIELDS' },
        { label: 'Pull Usage Data', value: 'PULL_USAGE_DATA' },
      ],
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
      },
      weekdays: {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday',
      },
      months: {
        0: 'January',
        1: 'February',
        2: 'March',
        3: 'April',
        4: 'May',
        5: 'June',
        6: 'July',
        7: 'August',
        8: 'September',
        9: 'October',
        10: 'November',
        11: 'December',
      },
      selectedUsers: [],
      selectedUser: null,
      selectedSlackForms: null,
      showOrgList: false,
      showCommandList: false,
      filtering: false,
      teamOrUser: [{ name: 'team' }, { name: 'user' }],
      selectedTeamOrUser: null,
      selectedViewedTeam: null,
      selectedTeam: null,
      selectedFilter: null,
      selectedDeactivateOrg: null,
      filterByDay: 30,
      usersFilteredByDays: [],
      deleteOpen: false,
      trialUsers: [],
      teamList: [],
      activeFilters: [],
      orgUsers: [],
      orgSlackForms: [],
      setFilters: {},
      filteredOrgUsers: [],
      filteredOrgSlackForms: [],
      filteredOrgMeetingWorkflows: [],
      filteredOrgSlackFormInstances: [],
      filteredOrgAlerts: [],
      orgSlackFormInstances: null,
      selectedCommand: '',
      loading: true,
      commandButtonLoading: false,
      editOpModalOpen: false,
      modalInfo: null,
      displayCommandModal: false,
      contentModalInfo: null,
      orgAlerts: null,
      contentType: '',
      states: ['ACTIVE', 'INACTIVE'],
      stateActive: null,
      ignoreEmails: [],
      hasProducts: false,
      orgMeetingWorkflows: null,
      selected_org: null,
      old_selected_org: null,
      adminTasks: null,
      modalName: '',
      page: null,
      organizations: [],
      invitedUsers: null,
      activeUsers: null,
      filterText: '',
      showAdminTasks: false,
      newAdmin: null,
      admin: null,
      selectedAction: null,
      actionOptions: [
        {label: 'Users Overview', action: () => this.openModal('usersOverview', this.filteredOrgUsers)},
        {label: 'Forms', action: () => this.goToSlackForms() /*this.openModal('slackForm', this.selectedSlackForms)*/},
        {label: 'Submissions', action: () => this.goToSlackFormInstace()},
        {label: 'Alerts', action: () => this.goToAlerts()},
      ],
      inviteActions: [
          {
            label: 'Uninvite', 
            action: (thisPassed, member) => {
              if ((member.isAdmin || member.is_admin)) {
                thisPassed.$toast('Cannot uninvite the current admin.', {
                  timeout: 2000,
                  position: 'top-left',
                  type: 'error',
                  toastClassName: 'custom',
                  bodyClassName: ['custom'],
                })
                return
              }
              if (!member.isActive && !member.is_active) {
                thisPassed.$toast('User already deactivated.', {
                  timeout: 2000,
                  position: 'top-left',
                  type: 'error',
                  toastClassName: 'custom',
                  bodyClassName: ['custom'],
                })
                return
              }
              thisPassed.openUninviteModal(member.id)
            },
          },
          {
            label: 'Change Team',
            action: (thisPassed, member) => {
              if ((member.isAdmin || member.is_admin)) {
                thisPassed.$toast('Cannot change the team of the current admin.', {
                  timeout: 2000,
                  position: 'top-left',
                  type: 'error',
                  toastClassName: 'custom',
                  bodyClassName: ['custom'],
                })
                return
              }
              this.selectedUsers = [member]
              this.selectedTeam = this.teamList.filter(team => team.id === member.team)[0]
              this.handleEdit()
            },
          },
          {
            label: 'Make Team Lead',
            action: (thisPassed, member) => {
              if (member.team === this.admin.team) {
                thisPassed.$toast('Cannot change the team lead of admin\'s team.', {
                  timeout: 2000,
                  position: 'top-left',
                  type: 'error',
                  toastClassName: 'custom',
                  bodyClassName: ['custom'],
                })
                return
              }
              this.selectedTeamLead = member
              this.changeTeamLeader()
            },
          },
      ],
      pulseLoading: false,
      changeAdminConfirmModal: false,
      team: CollectionManager.create({ ModelClass: User }), // might need to change based off of org users
      newTeam: false,
      changeTeam: false,
      changeTeamLead: false,
      editTeam: false,
      inviteOpen: false,
      manageTeamSelected: true,
      teamLead: null,
      teamName: '',
      selectedTeamLead: null,
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
    filteredOrganizations() {
      if (!this.filterText) {
        return this.filteredActiveOrganizations
      } else {
        return this.filteredActiveOrganizations.filter((org) =>
          org.name.toLowerCase().includes(this.filterText.toLowerCase()),
        )
      }
    },
    selectedTeamUsers() {
      if (this.selectedViewedTeam) {
        return this.orgUsers.filter(user => user.team === this.selectedViewedTeam.id)
      } else return []
    },
    filteredActiveOrganizations() {
      return this.organizations.filter(org => org.state === 'ACTIVE')
    },
    activeTrialUsers() {
      return this.trialUsers.filter(user => user.updates_this_month >= 10)
    },
    dayTrialUsers() {
      const trialUsers = this.trialUsers.filter(user => user.days_active <= this.filterByDay)
      return trialUsers.sort((a, b) => a.days_active - b.days_active)
    }
  },
  mounted() {
    this.stateActive = this.user.organizationRef.state
    this.hasProducts = this.user.organizationRef.hasProducts ? {label: 'Yes', value: true} : {label: 'No', value: false}
    this.ignoreEmails = this.user.organizationRef.ignoreEmailRef
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    getUserName(id) {
      const user = this.orgUsers.filter((user) => user.id == id)[0]
      return user ? `${user.first_name} ${user.last_name}` : '-'
    },
    filtersLabel(prop) {
      if (this.selectedTeamOrUser) {
        return this.selectedTeamOrUser.name === 'team' ? prop.name : prop.email
      }
    },
    resetFilters() {
      this.activeFilters = []
      this.selectedFilter = null
      this.filteredOrgUsers = this.orgUsers
      this.filteredOrgSlackForms = this.orgSlackForms
      this.filteredOrgMeetingWorkflows = this.orgMeetingWorkflows
      this.filteredOrgSlackFormInstances = this.orgSlackFormInstances
      this.filteredOrgAlerts = this.orgAlerts
    },
    handleNewTeam() {
      this.newTeam = !this.newTeam
    },
    handleChangeTeam() {
      this.changeTeam = !this.changeTeam
    },
    handleChangeTeamLead() {
      this.changeTeamLead = !this.changeTeamLead
    },
    handleInvite() {
      this.inviteOpen = !this.inviteOpen
    },
    handleEdit() {
      this.editTeam = !this.editTeam
    },
    handleCancel() {
      this.inviteOpen = false
      this.editTeam = false
      this.newTeam = false
      this.changeTeamLead = false
    },
    async createTeamSubmit() {
      this.pulseLoading = true
      if (!this.teamLead || !this.teamName) {
        setTimeout(() => {
          this.$toast('Please submit all info', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.pulseLoading = false
          return
        }, 200)
      } else {
        try {
          const data = {
            name: this.teamName,
            organization: this.selected_org.id,
            team_lead: this.teamLead.id,
          }
          const teamRes = await Organization.api.createNewTeam(data)
          const addTeamData = {
            users: [this.teamLead.id],
            team_id: teamRes.id,
          }
          await Organization.api.addTeamMember(addTeamData)
          this.orgUsers = await this.getAllOrgUsers(this.selected_org.id)
          this.team = this.orgUsers
          this.getStaffOrgs()
          setTimeout(() => {
            this.handleCancel()
            this.teamName = ''
            this.teamLead = ''
            this.$toast('Sucessfully submitted', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.pulseLoading = false
          }, 1400)
        } catch (e) {
          console.log(e)
          this.$toast('Error Creating Team', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }
    },
    async editTeamSubmit() {
      this.pulseLoading = true
      if (!this.selectedTeam || !this.selectedUsers.length) {
        setTimeout(() => {
          this.$toast('Please submit all info', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.pulseLoading = false
          return
        }, 200)
      } else {
        try {
          const userIds = this.selectedUsers.map((user) => user.id)
          const addTeamData = {
            users: userIds,
            team_id: this.selectedTeam.id,
          }
          await Organization.api.addTeamMember(addTeamData)
          this.orgUsers = await this.getAllOrgUsers(this.selected_org.id)
          this.team = this.orgUsers
          setTimeout(() => {
            this.handleCancel()
            this.selectedUsers = []
            this.selectedTeam = ''
            this.$toast('Sucessfully submitted', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.pulseLoading = false
          }, 1400)
        } catch (e) {
          console.log('Error: ', e)
          this.$toast('Error Creating Team', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }
    },
    async changeTeamLeader() {
      this.pulseLoading = true
      if (!this.selectedTeamLead) {
        setTimeout(() => {
          this.$toast('Please submit all info', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.pulseLoading = false
          return
        }, 200)
      } else {
        try {

          const addTeamData = {
            team_lead: this.selectedTeamLead.id,
            id: this.selectedViewedTeam.id,
          }
          await Organization.api.changeTeamLead(addTeamData)
          this.orgUsers = await this.getAllOrgUsers(this.selected_org.id)
          this.team = this.orgUsers
          setTimeout(() => {
            this.handleCancel()
            this.selectedUsers = []
            this.selectedTeam = ''
            this.$toast('Sucessfully submitted', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.pulseLoading = false
          }, 1400)
        } catch (e) {
          console.log('Error: ', e)
          this.$toast('Error Creating Team', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.pulseLoading = false
        }
      }
    },
    getWeekdays(daysArr) {
      const weekDays = []
      for (let i = 0; i < daysArr.length; i++) {
        weekDays.push(this.weekdays[daysArr[i]])
      }
      return weekDays
    },
    selectOrg(org) {
      this.selected_org = org
      this.clearUsersAndSlackForm()
      this.closeListSelect()
      this.resetFilters()
    },
    clearUsersAndSlackForm() {
      this.selectedSlackForms = null
      this.selectedUser = null
    },
    closeFilters() {
      this.filtering = false
    },
    addingFilter() {
      if (this.filtering === true) {
        this.filtering = false
      } else {
        this.filtering = true
      }
    },
    applyFilter(value) {
      this.getFilteredObjects(value)
      this.activeFilters.push(this.selectedFilter)
      this.selectedFilter = null
      this.selectedTeamOrUser = null
      this.filtering = false
    },
    async getFilteredObjects(value) {
      if (value) {
        const newValue = value.email ? value.email : value.name
        this.setFilters[this.activeFilters.length] = [this.selectedTeamOrUser.name, newValue]
      }
      if (this.selectedTeamOrUser.name === 'team') {
        const userIdsList = []
        this.filteredOrgUsers = this.orgUsers.filter((item) => {
          if (item.team === value.id) {
            userIdsList.push(item.id)
            return item
          }
        })
        this.filteredOrgSlackForms = this.orgSlackForms.filter((item) => item.team === value.id)
        this.filteredOrgMeetingWorkflows = this.orgMeetingWorkflows.filter((item) =>
          userIdsList.includes(item.user),
        )
        this.filteredOrgSlackFormInstances = this.orgSlackFormInstances.filter((item) =>
          userIdsList.includes(item.user),
        )
        this.filteredOrgAlerts = this.orgAlerts.filter((item) => userIdsList.includes(item.user))
      } else {
        this.filteredOrgUsers = this.orgUsers.filter((item) => {
          if (item.id === value.id) {
            return item
          }
        })
        this.filteredOrgSlackForms = this.orgSlackForms.filter((item) => item.team === value.team)
        this.filteredOrgMeetingWorkflows = this.orgMeetingWorkflows.filter(
          (item) => item.user === value.id,
        )
        this.filteredOrgSlackFormInstances = this.orgSlackFormInstances.filter(
          (item) => item.user === value.id,
        )
        this.filteredOrgAlerts = this.orgAlerts.filter((item) => item.user === value.id)
      }
    },
    async getAllOrgUsers(orgId) {
      const res = await User.api.getAllOrgUsers(orgId)
      return res
    },
    async getTasks() {
      try {
        let res = await User.api.getTasks()
        const tasks = JSON.parse(res.tasks)
        this.adminTasks = tasks
      } catch (e) {
        console.log(e)
      }
    },
    selectAction(e) {
      if (e.action) {
        e.action()
        setTimeout(() => {
          this.selectedAction = null
        }, 0)
      }
    },
    async getStaffOrgs() {
      try {
        let res = await Organization.api.getStaffOrganizations()
        this.organizations = res
        if (this.selected_org) {
          const orgForTeam = this.organizations.filter(org => org.id === this.selected_org.id)[0]
          this.teamList = orgForTeam.teams_ref
        }
      } catch (e) {
        console.log(e)
      }
    },
    checkDecimals(value) {
      if (Number(value) === NaN) {
        return true
      }
      const checkArr = value.toString().split('.')
      if (checkArr[1] === undefined) {
        return true
      }
      const afterDec = checkArr[1].toString()
      for (let i = 0; i < afterDec.length; i++) {
        const digit = afterDec[i]
        if (digit !== '0') {
          return true
        }
      }
      return false
    },
    selectCommand(cmd) {
      this.selectedCommand = cmd
      this.closeListSelect()
      this.runCommand()
    },
    async runCommand() {
      if (!this.selectedCommand || !this.selectedCommand.value) {
        this.$toast('Please select a command.', {
          type: 'error',
          timeout: 3000,
        })
        return
      }
      try {
        this.commandButtonLoading = true
        const res = await User.api.callCommand(this.selectedCommand.value)
        if (res.data) {
          const newResContent = []
          const newResObjects = {}
          for (let key in res.data.totals) {
            const item = res.data.totals[key]
            newResObjects[key] = {}
            newResObjects[key].total = item
          }
          for (let key in res.data.org) {
            const item = res.data.org[key]
            for (let key2 in item) {
              item[key2].name = key2
              for (let key3 in item[key2].users) {
                item[key2].users[key3].userName = key3
              }
            }
            newResObjects[key].orgs = item
          }
          for (let key in newResObjects) {
            const item = newResObjects[key]
            item['date'] = key
            newResContent.unshift(item)
          }
          this.contentModalInfo = newResContent
          this.displayCommandModal = true
          this.contentType = 'PullUsageData'
        } else {
          if (res.success) {
            this.$toast(res['message'], {
              type: 'success',
              timeout: 3000,
            })
          } else {
            this.$toast('Something went wrong. Please try again.', {
              type: 'error',
              timeout: 3000,
            })
          }
        }
        this.commandButtonLoading = false
      } catch (e) {
        console.log(e)
        this.$toast('Something went wrong. Please try again.', {
          type: 'error',
          timeout: 3000,
        })
        this.commandButtonLoading = false
      }
    },
    async postOrgUpdates() {
      let noSpacesEmails = ''
      for (let i = 0; i < this.ignoreEmails.length; i++) {
        if (this.ignoreEmails[i] !== ' ') {
          noSpacesEmails += this.ignoreEmails[i]
        }
      }
      const orgUpdates = {
        state_active: this.stateActive,
        has_products: this.hasProducts.value,
        ignore_emails: noSpacesEmails,
        org_id: this.selected_org.id,
      }
      try {
        const res = await Organization.api.orgUpdate(orgUpdates)
        this.getStaffOrgs()
        // this.$toast(
        //   'Organization Updated. Please wait a few seconds and then hard refresh (ctrl + shift + r)',
        //   {
        //     type: 'success',
        //     timeout: 4000,
        //   },
        // )
        this.$router.go()
      } catch (e) {
        console.log('error: ', e)
        this.$toast('Something went wrong.', {
          type: 'error',
          timeout: 3000,
        })
      }
    },
    weekDay(input) {
      let newer = new Date(input)
      return this.days[newer.getDay()]
    },
    getMonth(input) {
      let newer = new Date(input)
      return this.months[newer.getMonth()]
    },
    getYear(input) {
      let newer = new Date(input)
      return newer.getFullYear()
    },
    getTime(input) {
      let newer = new Date(input)
      let hours = newer.getHours()
      let minutes = newer.getMinutes()
      if (minutes < 10) {
        let newMinutes = '0' + minutes
        minutes = newMinutes
      }
      let afternoon = false
      if (hours === 0) {
        hours = 12
      } else if (hours === 12) {
        afternoon = true
      } else if (hours > 12) {
        hours = hours - 12
        afternoon = true
      }
      if (afternoon) {
        return `${hours}:${minutes} PM`
      } else {
        return `${hours}:${minutes} AM`
      }
    },
    customUserLabel(user) {
      return user.full_name.trim() ? user.full_name : user.email
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    goBack() {
      this.selected_org = this.old_selected_org
      this.old_selected_org = null
      this.page = null
    },
    goBackFromTeam() {
      this.page = null
    },
    closeListSelect() {
      this.showOrgList = false
      this.showCommandList = false
    },
    goToTeamManager() {
      // this.old_selected_org = this.selected_org
      // this.selected_org = null
      this.page = 'TeamManager'
    },
    goToSlackForms() {
      this.old_selected_org = this.selected_org
      this.selected_org = null
      this.page = 'SlackForm'
    },
    goToSlackFormInstace() {
      this.old_selected_org = this.selected_org
      this.selected_org = null
      this.page = 'SlackFormInstance'
    },
    goToMeetingWorkflow() {
      this.old_selected_org = this.selected_org
      this.selected_org = null
      this.page = 'MeetingWorkflow'
    },
    goToAlerts() {
      this.old_selected_org = this.selected_org
      this.selected_org = null
      this.page = 'OrgAlerts'
    },
    openModal(name, data) {
      console.log('data', data)
      if ((!data || !Object.keys(data).length) && name !== 'task') {
        this.$toast('Please select an item', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      this.modalName = name
      this.modalInfo = data
      if (this.modalName === 'usersOverview') {
        this.invitedUsers = this.modalInfo.filter((user) => !user.first_name)
        this.activeUsers = this.modalInfo.filter((user) => user.is_active)
      }
      this.editOpModalOpen = true
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
      this.modalName = ''
      this.modalInfo = null
      this.invitedUsers = null
      this.activeUsers = null
      this.selectedUser = null
    },
    resetCommandsEdit() {
      this.displayCommandModal = !this.displayCommandModal
      this.contentType = ''
      this.contentModalInfo = null
    },
    onCopy: function () {
      this.$toast('Copied', {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    },
    onError: function () {
      this.$toast('Error copying template', {
        timeout: 2000,
        position: 'top-left',
        type: 'error',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    },
    handleConfirm() {
      this.changeAdminConfirmModal = !this.changeAdminConfirmModal
    },
    handleConfirmCancel() {
      this.changeAdminConfirmModal = false
      this.newAdmin = this.admin
    },
    async changeAdminSubmit() {
      this.pulseLoading = true
      if (!this.newAdmin || this.newAdmin.is_admin) {
        setTimeout(() => {
          this.$toast('Please choose a new admin', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.pulseLoading = false
          return
        }, 200)
      } else {
        try {
          const data = {
            new_admin: this.newAdmin.id,
          }
          const teamRes = await Organization.api.changeAdmin(data)
          setTimeout(() => {
            this.handleConfirmCancel()
            this.$toast('Sucessfully submitted', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.pulseLoading = false
            this.$router.go()
          }, 1400)
        } catch (e) {
          console.log('Error: ', e)
          this.$toast('Error changing admin', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.pulseLoading = false
        }
      }
    },
    getObjString(obj, i) {
      const orgs = obj.orgs
      let orgsString = ''
      for (let key in orgs) {
        const org = orgs[key]
        const users = org.users
        let usersStr = '{'
        for (let key2 in users) {
          const user = users[key2]
          usersStr += `
          "${key2}": {
            "creates": "${user['creates']}",
            "session average": "${user['session average']}",
            "total sessions": "${user['total sessions']}",
            "updates": "${user['updates']}",
            "userName": "${user['userName']}"
          },`
        }
        usersStr = usersStr.slice(0, usersStr.length - 1)
        usersStr += `
          }`
        orgsString += `
        "${key}": {
          "average total sessions": "${org['average total sessions']}",
          "creates": "${org['creates']}",
          "name": "${org['name']}",
          "session average": "${org['session average']}",
          "updates": "${org['updates']}",
          "users": ${usersStr}
        },`
      }
      orgsString = orgsString.slice(0, orgsString.length - 1)
      const stringObj = `
      "${i}": {
        "date": "${obj.date}",
        "total": {
          "creates": {
            "accounts": "${obj.total.creates.accounts}",
            "contacts": "${obj.total.creates.contacts}",
            "opportunities": "${obj.total.creates.opportunities}",
            "products": "${obj.total.creates.products}",
            "total": "${obj.total.creates.total}"
          },
          "updates": {
            "alert": "${obj.total.updates.alert}",
            "command": "${obj.total.updates.command}",
            "meeting": "${obj.total.updates.meeting}",
            "pipeline": "${obj.total.updates.pipeline}",
            "total": "${obj.total.updates.total}"
          },
          "users": "${obj.total.users}",
          "workflows": "${obj.total.workflows}"
        },
        "orgs": {${orgsString}
        }
      }
      `
      return stringObj
    },
    deactivateOrg() {
      if (!this.selectedDeactivateOrg) {
        this.$toast('Please select an org to delete', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      this.deleteOpen = true
    },
    deleteClose() {
      this.deleteOpen = false
    },
    async onDeleteOrg() {
      this.deleteOpen = !this.deleteOpen
      try {
        const res = await Organization.api.orgDeactivate(this.selectedDeactivateOrg.id)
        this.getStaffOrgs()
        this.selectedDeactivateOrg = null
        this.$toast('Organization removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch {
        this.$toast('Error removing organization', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getTrialUsers() {
      try {
        const res = await User.api.getTrialUsers()
        this.trialUsers = res
      } catch(e) {
        console.log('Error in getTrialUsers', e)
      }
    },
    formatCopyObject(obj) {
      let string = '{'
      if (obj.length) {
        for (let i = 0; i < obj.length; i++) {
          string += this.getObjString(obj[i], i + 1)
          string += ','
        }
        string = string.slice(0, string.length - 1)
      } else {
        string += this.getObjString(obj, 1)
      }
      string += '}'
      return string
    },
    slackFormLabel({ form_type, resource }) {
      let formattedFormType = form_type[0]
      for (let i = 1; i < form_type.length; i++) {
        formattedFormType += form_type[i].toLowerCase()
      }
      return `${formattedFormType} ${resource}`
    },
  },
  created() {
    this.getTasks()
    this.getStaffOrgs()
    this.getTrialUsers()
  },
  watch: {
    async selected_org() {
      if (this.selected_org) {
        this.loading = false
        this.filterText = ''
        this.ignoreEmails = this.selected_org.ignore_email_ref
        this.hasProducts = this.selected_org.has_products ? {label: 'Yes', value: true} : {label: 'No', value: false}
        this.stateActive = this.selected_org.state
        this.orgUsers = await this.getAllOrgUsers(this.selected_org.id)
        this.orgSlackForms = await SlackOAuth.api.getStaffForms(this.selected_org.id)
        this.orgMeetingWorkflows = await MeetingWorkflows.api.getStaffMeetings(this.selected_org.id)
        this.orgSlackFormInstances = await SlackOAuth.api.getStaffFormInstances(
          this.selected_org.id,
        )
        this.orgAlerts = await AlertTemplate.api.getAdminAlerts(this.selected_org.id)
        this.teamList = this.selected_org.teams_ref
        this.admin = this.orgUsers.filter(user => user.is_admin)[0]
        this.newAdmin = this.admin
        this.selectedViewedTeam = this.teamList.filter(team => team.id === this.admin.team)[0]
        this.filteredOrgUsers = this.orgUsers
        this.team = this.orgUsers
        this.filteredOrgSlackForms = this.orgSlackForms
        this.selectedSlackForms = this.filteredOrgSlackForms[0]
        this.filteredOrgMeetingWorkflows = this.orgMeetingWorkflows
        this.filteredOrgSlackFormInstances = this.orgSlackFormInstances
        this.filteredOrgAlerts = this.orgAlerts
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.staff {
  margin-top: 3rem;
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-left: 60px;
}
.staff__main_page {
  width: 80vw;
  margin-left: 1rem;
}
p {
  font-size: 14px;
}
h1 {
  margin-top: -1px;
  margin-left: -0.1rem;
  font-size: 38px;
}
.form__list {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  margin-left: 1rem;
  margin-top: 1rem;
  width: 82vw;
}
ul {
  margin: 0;
  padding: 0;
}
.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: bold;
  font-size: 14px;
  border: none;
  cursor: pointer;
}
.sized {
  height: 3em;
  align-self: center;
}
input[type='search'] {
  margin: 0 1rem 0 0;
  background-color: white;
  padding: 4px;
}
input[type='search']:focus {
  outline: none;
}
::placeholder {
  color: $very-light-gray;
}
.wide {
  display: flex;
  justify-content: center;
  width: 100%;
  background-color: white;
}
.gray-border {
  border: 1px solid #e8e8e8;
  border-radius: 5px;
}
.back {
  margin: 1rem 0;
  text-decoration: underline;
  cursor: pointer;
}
.modal-container {
  background-color: $white;
  overflow: auto;
  width: 60vw;
  height: 88vh;
  align-items: center;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;

  &__header {
    display: flex;
    justify-content: space-between;
    padding-left: 0.75rem;
    border-bottom: 1px solid #e8e8e8;
    img {
      filter: invert(80%);
      height: 1.25rem;
      margin-top: 0.75rem;
      margin-right: 0.5rem;
      cursor: pointer;
    }
  }
  &__body {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    margin-top: 1vh;
    padding: 0 1rem;
    min-height: 28vh;
  }
  // &__footer {
  //   display: flex;
  //   align-items: flex-end;
  //   justify-content: flex-end;
  //   position: sticky;
  //   height: 8vh;
  //   padding: 0.5rem;
  // }
}
.light-back {
  background-color: $white-green;
}
.pure-white {
  background-color: #ffffff;
}
.click {
  cursor: pointer;
  transition: all 0.25s;
}
.click:hover {
  text-shadow: 1px 1px 0px lightgray;
  transform: scale(1.015);
}
.click_width {
  width: max-content;
}
.padding {
  padding: 0.25rem 1rem;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
// .copy-margin {
//   margin-right: 1rem;
// }
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
}
.border-bottom {
  border-bottom: 1.25px solid $soft-gray;
}
.left-actions {
  width: 40vw;
  border-right: 1px solid $light-gray;
}
.right-actions {
  width: 35vw;
  justify-self: flex-start;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  letter-spacing: 1px;
  h4 {
    font-size: 20px;
  }
}
.logo {
  height: 20px;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.note-section {
  padding: 0.25rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 19px;
    font-weight: bolder;
    letter-spacing: 0.6px;
    color: $base-gray;
    padding: 0;
  }
  &__small_title {
    font-size: 17px;
    font-weight: bolder;
    letter-spacing: 0.6px;
    color: $base-gray;
    padding: 0;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
    border-left: 2px solid $dark-green;
    padding-left: 32px;
    font-size: 16px;
    white-space: pre-line;
  }
  &__date {
    color: $mid-gray;
    font-size: 12px;
    margin-top: -14px;
    margin-bottom: 8px;
    letter-spacing: 0.6px;
  }
}
.underline {
  text-decoration: underline;
  font-size: 1.05rem;
}
.invite-list {
  &__container {
    background-color: $white;
    border: 1px solid #e8e8e8;
    color: $base-gray;
    width: 82vw;
    // height: 60vh;
    overflow: scroll;
    padding: 1.5rem 1.5rem 1.5rem 1rem;
    margin-left: 1rem;
    border-radius: 5px;
    display: flex;
    align-items: flex-start;
    flex-direction: column;
  }
  &__section {
    &__container {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      margin-bottom: 0.5rem;
      height: 6vh;
    }
    &__item {
      margin-right: 1rem;
    }
  }
  &__status {
    font-size: 0.75rem;
  }
}
.line-up {
  width: 30%;
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 28%;
  margin-top: -7rem;
  margin-left: -2rem;
  z-index: 1;
}
.z-more {
  z-index: 2;
}
.added-collection {
  background-color: white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  width: 45%;
  margin-bottom: 1rem;
  transition: all 0.25s;
  &__header {
    max-height: 3rem;
    margin: 0;
    padding: 1.75rem 1rem;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 2px solid $soft-gray;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 5rem;
    font-size: 13px;
  }
  &__footer {
    display: flex;
    align-items: center;
    height: 3rem;
    padding: 1rem;
    font-size: 14px;
    justify-content: space-evenly;
  }
}
.added-collection:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
  transform: scale(1.015);
}
.separator {
  margin-top: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid black;
}
.green {
  color: $dark-green;
  background-color: $white-green;
  font-size: 0.75rem;
  padding: 2px 4px;
  border-radius: 4px;
  margin-left: 4px;
}
.invite-list-users {
  &__container {
    background-color: $white;
    // border: 1px solid #e8e8e8;
    color: $base-gray;
    width: 92vw;
    height: 60vh;
    overflow: scroll;
    padding: 1.5rem 0rem 1.5rem 1rem;
    border-radius: 5px;
    display: flex;
    align-items: flex-start;
    flex-direction: column;
  }
  &__section {
    &__container {
      width: 100%;
      display: flex;
      // margin-bottom: 0.5rem;
      z-index: 2;
      margin-left: 16px;
    }
    &__item {
      width: 33%;
      overflow-wrap: break-word;
    }
  }
  &__status {
    img {
      margin-right: 16px;
    }
  }
}
.col {
  display: flex;
  flex-direction: column;
}
.grayscale {
  filter: grayscale(99%);
}
.pipeline-header {
  font-size: 11px;
  color: $light-gray-blue;
  margin-left: 4px;
}
.text-button {
  border: none;
  font-size: 13px;
  background-color: transparent;
  margin-right: 8px;
  color: $base-gray;
  letter-spacing: 0.75px;
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 10vh;
  left: 88px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 70vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  letter-spacing: 0.75px;
  &__title {
    position: sticky;
    top: 0;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.75px;
    padding-left: 0.75rem;
    font-size: 16px;
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    cursor: pointer;
    img {
      margin-top: 2px;
    }
  }
  &__sub-title {
    font-size: 12px;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    margin-top: 1rem;
    color: $base-gray;
    cursor: pointer;
    width: 100%;
    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.list-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  border-radius: 6px;
  color: $base-gray;
  cursor: pointer;
  font-size: 12px;
  letter-spacing: 0.75px;
}
.list-button:hover {
  color: $dark-green;
  background-color: $off-white;
}
.main {
  border: none;
  height: 5vh;
  max-width: 10vw;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: $white-green;
  cursor: pointer;
  color: $dark-green;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}
.main:hover {
  overflow: visible;
  white-space: normal;
  max-width: none;
}

main > span {
  display: none;
}
main:hover > span {
  display: block;
}
.add-filter-button {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: transparent;
  cursor: pointer;
  color: $base-gray;
  letter-spacing: 0.75px !important;

  img {
    filter: invert(70%);
  }
}
.filter-selection {
  position: absolute;
  top: 6vh;
  left: 0;
  border-radius: 0.33rem;
  background-color: $white;
  min-width: 24vw;
  padding: 1rem 1rem 0rem 1rem;
  overflow: visible;
  box-shadow: 1px 1px 7px 2px $very-light-gray;

  &__body {
    display: flex;
    align-items: center;
    justify-content: flex-start;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    margin-top: 1.5rem;
    height: 3rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      font-size: 13px;
      padding-top: 0.5rem;
    }
  }
}
.org-title {
  // color: $dark-green;
  // text-decoration: underline;
  font-weight: 900;
  font-size: 1.5rem;
  margin-top: 0;
  margin-bottom: 0.2rem;
}
.org-subtitle {
  margin-top: 0; 
  margin-left: 0.2rem;
  color: $dark-green;
  font-size: 0.9rem;
}
.yellow-background {
  background-color: yellow;
}
.search-bar {
  background-color: white;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border-radius: 8px;
  // margin-top: 16px;
  margin-left: 4px;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 15vw;
  // letter-spacing: 0.75px;
  border: none;
  padding: 2px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
.header {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  height: 8vh;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
}
.invite-form {
  border: none;
  border-radius: 0.75rem;
  min-width: 37vw;
  // min-height: 64vh;
  display: flex;
  align-items: center;
  justify-content: space-around;
  flex-direction: column;
  background-color: white;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
  }
  &__subtitle {
    text-align: left;
    font-size: 16px;
    margin-left: 1rem;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.modal-form {
  width: 100%;
  background-color: $white;
  height: 40vh;
  // justify-content: space-evenly;
}
.confirm-form {
  width: 37vw;
  height: 38vh;
}
.form-margin-small {
  margin-top: 10rem;
}
.invite_button {
  display: flex;
  flex-direction: row;
  color: $base-gray;
  background-color: white;
  border-radius: 6px;
  transition: all 0.25s;
  padding: 8px 12px;
  margin-left: 8px;
  font-size: 14px;
  letter-spacing: 0.75px;
  border: 1px solid #e8e8e8;
}
.invite_button:disabled {
  display: flex;
  flex-direction: row;
  color: $base-gray;
  background-color: $soft-gray;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 8px 12px;
  font-weight: 400px;
  font-size: 14px;
  border: 1px solid #e8e8e8;
}

.invite_button:disabled:hover {
  color: $base-gray;
  cursor: text;
}

.invite_button:hover {
  cursor: pointer;
  color: $dark-green;
}
.modal-button {
  @include primary-button();
  box-shadow: none;
  margin-top: 1.5rem;
  height: 2.5rem;
  width: 19rem;
  font-size: 14px;
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
.invite-users {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  text-align: center;
  margin-top: 8px;
  // margin-left: 60px;
  padding-bottom: 1rem;
  border-top-left-radius: 4px;

  background-color: white;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 60vw;
    padding: 0.25rem;
  }

  &__inviter {
    margin-top: 8px;
  }
}
.modal-header {
  width: 100%;
  margin-top: -1.5rem;
  display: flex;
  justify-content: space-between;
}
.template-input {
  border: 1px solid #ccc;
  border-bottom: none;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;
  padding-left: 1rem;
  height: 44px;
  width: 40vw;
  font-family: inherit;
  margin-bottom: 1rem;
}
.template-input:focus {
  outline: none;
}
.modal-input {
  width: 15vw;
  height: 2.5rem;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
}
.modal-input:focus {
  outline: none;
}
.modal-input::placeholder {
  // color: #35495e;
  color: $very-light-gray;
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
.profile-info {
  position: absolute;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-left: 32px;
  padding-bottom: 8px;
  letter-spacing: 0.75px;
  width: 100%;
  border-bottom: 1px solid $soft-gray;

  &__img {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background-color: $off-white;
    border: 1px solid $soft-gray;
    border-radius: 100%;
    height: 19vh;
    width: 19vh;
  }

  &__body {
    color: $base-gray;
    margin-left: 8px;
    margin-top: 16px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-end;

    h2,
    h3,
    p,
    small {
      padding: 0;
      margin: 0;
    }
    small {
      color: $light-gray-blue !important;
      margin-top: 6px;
    }
    h3 {
      margin-top: 6px;
    }
  }
}
.options {
  // border: 1px solid $soft-gray;
  top: 10vh;
  left: 20vw;
  padding: 16px 8px 8px 8px;
  border-radius: 6px;
  background-color: white;
  z-index: 20;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  font-size: 14px;
  letter-spacing: 0.75px;

  p {
    padding: 4px !important;
    margin-bottom: 6px !important;
    width: 100%;
    display: flex;
    align-items: flex-start;
  }
  p:hover {
    background-color: $off-white;
    color: $dark-green;
    border-radius: 6px;
    cursor: pointer;
  }

  &__section {
    margin: 0px 8px 8px -8px;
    padding: 8px 8px 8px 0px;
    display: flex;
    flex-direction: row;
    align-items: center;
  }
}
.invite-button {
  background-color: $dark-green;
  color: white;
  margin-top: 2.5rem;
  width: 15vw;
  font-size: 16px;
  box-shadow: none;
}
.main-content {
  margin-top: 15vh;
}
.team-top-container {
  display: flex; 
  flex-direction: row; 
  justify-content: space-between;
  align-items: center;
  margin-left: 1.2rem;
  border-bottom: 1px solid $very-light-gray;
  padding-bottom: 1rem;
  width: 75vw
}
</style>