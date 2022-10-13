<template>
  <div class="staff">
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
          <h2 class="modal-container__header">{{modalInfo.fields.task_name}}</h2>
          <div class="modal-container__body">
            <div class="note-section__body" style="margin-bottom: 1rem;">
              <div>
                <div class="underline">Task Params:</div>
                <div class="bottom-margin">{{modalInfo.fields.task_params ? modalInfo.fields.task_params : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Task Hash:</div>
                <div class="bottom-margin">{{modalInfo.fields.task_hash ? modalInfo.fields.task_hash : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Verbose Name:</div>
                <div class="bottom-margin">{{modalInfo.fields.verbose_name ? modalInfo.fields.verbose_name : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Priority:</div>
                <div class="bottom-margin">{{modalInfo.fields.priority || modalInfo.fields.priority === 0 ? modalInfo.fields.priority : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Run At:</div>
                <div class="bottom-margin">{{modalInfo.fields.run_at ? modalInfo.fields.run_at : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Repeat:</div>
                <div class="bottom-margin">{{modalInfo.fields.repeat || modalInfo.fields.repeat === 0 ? modalInfo.fields.repeat : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Repeat Until:</div>
                <div class="bottom-margin">{{modalInfo.fields.repeat_until ? modalInfo.fields.repeat_until : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Queue:</div>
                <div class="bottom-margin">{{modalInfo.fields.queue ? modalInfo.fields.queue : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Attempts:</div>
                <div class="bottom-margin">{{modalInfo.fields.attempts}}</div>
              </div>
              <div v-if="modalInfo.fields.failed_at">
                <div>
                  <div class="underline">Failed At:</div>
                  <div class="bottom-margin">{{modalInfo.fields.failed_at ? modalInfo.fields.failed_at : 'Null'}}</div>
                </div>
                <div>
                  <div class="underline">Last Error:</div>
                  <div class="bottom-margin">{{modalInfo.fields.last_error ? modalInfo.fields.last_error : 'Null'}}</div>
                </div>
              </div>
              <div>
                <div class="underline">Locked By:</div>
                <div class="bottom-margin">{{modalInfo.fields.locked_by ? modalInfo.fields.locked_by : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Locked At:</div>
                <div class="bottom-margin">{{modalInfo.fields.locked_at ? modalInfo.fields.locked_at : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Creator Content Type:</div>
                <div class="bottom-margin">{{modalInfo.fields.creator_content_type ? modalInfo.fields.creator_content_type : 'Null'}}</div>
              </div>
              <div>
                <div class="underline">Creator Object ID:</div>
                <div>{{modalInfo.fields.creator_object_id ? modalInfo.fields.creator_object_id : 'Null'}}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="modalName === 'slackForm'">
          <div class="modal-container__body">
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>
                  {{ modalInfo.form_type }} {{ modalInfo.resource }}
                </h4>
              </div>
            </div>
            <section class="note-section__body" style="margin-top: 1rem; margin-bottom: 1rem; white-space: normal; padding-left: 20px;">
              <!-- <div>{{modalInfo}}</div> -->
              <div v-for="(field, i) in modalInfo.fields_ref" :key="field.field">
                <div style="margin-top: 0.5rem; margin-bottom: 0.5rem;">
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
                  {{ modalInfo.template_ref.resource }} {{ modalInfo.template_ref.form_type }} by
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
              <p class="note-section__body">
                <span class="underline">Workflow ID:</span>
                {{ modalInfo.workflow ? modalInfo.workflow : 'None' }}
                <span class="underline">Update Source:</span>
                {{ modalInfo.update_source ? modalInfo.update_source : 'None' }}
                <span class="underline">User ID:</span>
                {{ modalInfo.user ? modalInfo.user : 'None' }}
                <span class="underline">Template ID:</span>
                {{ modalInfo.template ? modalInfo.template : 'None' }}
                <span class="underline">Saved Data:</span>
                {{ modalInfo.saved_data ? modalInfo.saved_data : 'None' }}
                <span class="underline">Previous Data:</span>
                {{ modalInfo.previous_data ? modalInfo.previous_data : 'None' }}
              </p>
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
              <br />
              <p class="note-section__date">
                End Time:
                {{
                  modalInfo.meeting_ref.end_time
                    ? `${weekDay(modalInfo.meeting_ref.end_time)} ${formatDateTime(
                        modalInfo.meeting_ref.end_time,
                      )} at ${getTime(modalInfo.meeting_ref.end_time)}`
                    : 'None'
                }}
              </p>
              <p class="note-section__body">
                <span class="underline">Meeting UUID: </span
                >{{
                  modalInfo.meeting_ref.meeting_uuid ? modalInfo.meeting_ref.meeting_uuid : 'None'
                }}
                <span class="underline">Account ID: </span
                >{{ modalInfo.meeting_ref.account_id ? modalInfo.meeting_ref.account_id : 'None' }}
                <span class="underline">Host ID: </span
                >{{ modalInfo.meeting_ref.host_id ? modalInfo.meeting_ref.host_id : 'None' }}
                <span class="underline">Operator ID: </span
                >{{
                  modalInfo.meeting_ref.operator_id ? modalInfo.meeting_ref.operator_id : 'None'
                }}
                <span class="underline">Status: </span
                >{{ modalInfo.meeting_ref.status ? modalInfo.meeting_ref.status : 'None' }}
                <span class="underline">Timezone: </span
                >{{ modalInfo.meeting_ref.timezone ? modalInfo.meeting_ref.timezone : 'None' }}
                <span class="underline">Start URL: </span
                >{{ modalInfo.meeting_ref.start_url ? modalInfo.meeting_ref.start_url : 'None' }}
                <span class="underline">Duration: </span
                >{{ modalInfo.meeting_ref.duration ? modalInfo.meeting_ref.duration : 'None' }}
                <span class="underline">Original Duration: </span
                >{{
                  modalInfo.meeting_ref.original_duration
                    ? modalInfo.meeting_ref.original_duration
                    : 'None'
                }}
                <span class="underline">Total Minutes: </span
                >{{
                  modalInfo.meeting_ref.total_minutes ? modalInfo.meeting_ref.total_minutes : 'None'
                }}
                <span class="underline">Recurrence: </span
                >{{ modalInfo.meeting_ref.recurrence ? modalInfo.meeting_ref.recurrence : 'None' }}
                <span class="underline">Join URL: </span
                >{{ modalInfo.meeting_ref.join_url ? modalInfo.meeting_ref.join_url : 'None' }}
                <span class="underline">Operator: </span
                >{{ modalInfo.meeting_ref.operator ? modalInfo.meeting_ref.operator : 'None' }}
                <span class="underline">Operation: </span
                >{{ modalInfo.meeting_ref.operation ? modalInfo.meeting_ref.operation : 'None' }}
                <span class="underline">Participants: </span
                >{{
                  modalInfo.meeting_ref.participants ? modalInfo.meeting_ref.participants : 'None'
                }}
                <span class="underline">Type: </span
                >{{ modalInfo.meeting_ref.type ? modalInfo.meeting_ref.type : 'None' }}
                <span class="underline">Zoom Account: </span
                >{{
                  modalInfo.meeting_ref.zoom_account ? modalInfo.meeting_ref.zoom_account : 'None'
                }}
              </p>
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
                <h4>{{ modalInfo.firstName }} {{ modalInfo.lastName }}</h4>
              </div>
            </div>
            <section class="note-section">
              <p class="note-section__title">General Info</p>
              <p class="note-section__body">
                <span class="underline">Email:</span>
                {{ modalInfo.email ? modalInfo.email : 'None' }}
                <span class="underline">Is Active:</span> {{ modalInfo.isActive }}
                <span class="underline">Is Invited:</span> {{ modalInfo.isInvited }}
                <span class="underline">Is Admin:</span> {{ modalInfo.isAdmin }}
                <span class="underline">Is Staff:</span> {{ modalInfo.isStaff }}
                <span class="underline">User Level:</span> {{ modalInfo.userLevel }}
                <span class="underline">Role:</span> {{ modalInfo.role }}
                <span class="underline">Timezone:</span> {{ modalInfo.timezone }}
                <span class="underline">Activated Managr Configs:</span>
                {{ modalInfo.activatedManagrConfigs ? modalInfo.activatedManagrConfigs : 'None' }}
              </p>
            </section>
            <section class="note-section">
              <p class="note-section__title">User Slack Integrations</p>
              <p class="note-section__body">
                <span class="underline">Slack ID:</span>
                {{ modalInfo.slackRef ? modalInfo.slackRef.slackId : 'None' }}
                <span class="underline">Channel:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.channel
                    ? modalInfo.slackAccount.channel
                    : 'None'
                }}
                <span class="underline">Organization Slack:</span>
                {{ modalInfo.organizationRef.slackIntegration }}
                <span class="underline">Is Onboarded:</span> {{ modalInfo.onboarding }}
                <span class="underline">Recap Channel:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.recapChannel
                    ? modalInfo.slackAccount.recapChannel
                    : 'None'
                }}
                <span class="underline">Recap Recievers:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.recapReceivers
                    ? modalInfo.slackAccount.recapReceivers
                    : 'None'
                }}
              </p>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Salesforce ({{
                  modalInfo.salesforceAccountRef ? modalInfo.salesforceAccountRef.id : 'None'
                }})
              </p>
              <p class="note-section__body">
                <span class="underline">SFDC ID:</span>
                {{
                  modalInfo.salesforceAccountRef && modalInfo.salesforceAccountRef.salesforceId
                    ? modalInfo.salesforceAccountRef.salesforceId
                    : 'None'
                }}
                <span class="underline">sobjects:</span>
                {{
                  modalInfo.salesforceAccountRef && modalInfo.salesforceAccountRef.sobjects
                    ? modalInfo.salesforceAccountRef.sobjects
                    : 'None'
                }}
                <span class="underline">Instance URL:</span>
                {{
                  modalInfo.salesforceAccountRef && modalInfo.salesforceAccountRef.instanceUrl
                    ? modalInfo.salesforceAccountRef.instanceUrl
                    : 'None'
                }}
                <span class="underline">Access Token:</span>
                {{
                  modalInfo.salesforceAccountRef && modalInfo.salesforceAccountRef.accessToken
                    ? modalInfo.salesforceAccountRef.accessToken
                    : 'None'
                }}
              </p>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Nylas ({{ modalInfo.nylasRef ? modalInfo.nylasRef.id : 'None' }})
              </p>
              <p class="note-section__body">
                <span class="underline">Access Token:</span>
                {{
                  modalInfo.nylasRef && modalInfo.nylasRef.accessToken
                    ? modalInfo.nylasRef.accessToken
                    : 'None'
                }}
                <span class="underline">Email:</span>
                {{
                  modalInfo.nylasRef && modalInfo.nylasRef.emailAddress
                    ? modalInfo.nylasRef.emailAddress
                    : 'None'
                }}
                <span class="underline">Event Calendar ID:</span>
                {{
                  modalInfo.nylasRef && modalInfo.nylasRef.eventCalendarId
                    ? modalInfo.nylasRef.eventCalendarId
                    : 'None'
                }}
                <span class="underline">Provider:</span>
                {{
                  modalInfo.nylasRef && modalInfo.nylasRef.provider
                    ? modalInfo.nylasRef.provider
                    : 'None'
                }}
              </p>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Zoom ({{ modalInfo.zoomRef ? modalInfo.zoomRef.id : 'None' }})
              </p>
              <p class="note-section__body">
                <span class="underline">Zoom ID:</span>
                {{
                  modalInfo.zoomRef && modalInfo.zoomRef.zoomId ? modalInfo.zoomRef.zoomId : 'None'
                }}
                <span class="underline">Timezone:</span>
                {{
                  modalInfo.zoomRef && modalInfo.zoomRef.timezone
                    ? modalInfo.zoomRef.timezone
                    : 'None'
                }}
                <span class="underline">Account ID:</span>
                {{
                  modalInfo.zoomRef && modalInfo.zoomRef.accountId
                    ? modalInfo.zoomRef.accountId
                    : 'None'
                }}
                <span class="underline">Access Token:</span>
                {{
                  modalInfo.zoomRef && modalInfo.zoomRef.accessToken
                    ? modalInfo.zoomRef.accessToken
                    : 'None'
                }}
                <span class="underline">Fake Meeting ID:</span>
                {{
                  modalInfo.zoomRef && modalInfo.zoomRef.fakeMeetingIdRef
                    ? modalInfo.zoomRef.fakeMeetingIdRef
                    : 'None'
                }}
              </p>
            </section>
            <section class="note-section">
              <p class="note-section__title">
                Slack Account ({{
                  modalInfo.slackAccount ? modalInfo.slackAccount.slackId : 'None'
                }})
              </p>
              <p class="note-section__body">
                <span class="underline">Slack ID:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.slackId
                    ? modalInfo.slackAccount.slackId
                    : 'None'
                }}
                <span class="underline">Channel:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.channel
                    ? modalInfo.slackAccount.channel
                    : 'None'
                }}
                <span class="underline">Zoom Channel:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.zoomChannel
                    ? modalInfo.slackAccount.zoomChannel
                    : 'None'
                }}
                <span class="underline">Recap Receivers:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.recapReceivers
                    ? modalInfo.slackAccount.recapReceivers
                    : 'None'
                }}
                <span class="underline">Real Time Alert Configs:</span>
                {{
                  modalInfo.slackAccount && modalInfo.slackAccount.realtimeAlertConfigs
                    ? modalInfo.slackAccount.realtimeAlertConfigs
                    : 'None'
                }}
              </p>
            </section>
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
              <button
                class="green_button sized copy-margin"
                v-clipboard:copy="formatCopyObject(contentModalInfo)"
                v-clipboard:success="onCopy"
                v-clipboard:error="onError"
              >
                <!-- <img src="@/assets/images/copy.svg" class="invert" style="height: 1.25rem" alt="" /> -->
                Copy All
              </button>
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
                  content.total && content.total.updates.alert !== null
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
    <div class="staff__drawer">
      <h3>Quick Commands</h3>
      <div class="command_dropdown">
        <Multiselect
          placeholder="Select Command"
          style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
          v-model="selectedCommand"
          :options="commandOptions"
          openDirection="below"
          selectLabel="Enter"
          track-by="value"
          label="label"
        >
          <template slot="noResult">
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>
        <button class="green_button sized" @click="runCommand">></button>
      </div>
      <h3>Organizations</h3>
      <Multiselect
        placeholder="Select Organization"
        @select="clearUsersAndSlackForm"
        style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
        v-model="selected_org"
        :options="organizations /*.list*/"
        openDirection="below"
        selectLabel="Enter"
        label="name"
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>
    </div>
    <div class="staff__main_page">
      <template v-if="selected_org && selected_org.id">
        <div v-if="loading">Loading</div>
        <template v-else>
          <!-- <div style="border-bottom: 1px solid black; margin-left: 1rem"> -->
          <div class="invite-list__container">
            <img class="back-logo" style="right: 18%; bottom: 60%" src="@/assets/images/logo.png" />
            <div class="invite-list__section__container">
              <div class="line-up">
                <div class="invite-list__section__item">State</div>
              </div>
              <div>
                <Multiselect
                  placeholder="State"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
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
                <div class="invite-list__section__item">Ignore Emails</div>
              </div>
              <div class="z-more" style="width: 48%">
                <input
                  class="wide gray-border z-more"
                  type="search"
                  v-model="ignoreEmails"
                  placeholder="Ignore Emails"
                />
              </div>
            </div>
            <div class="invite-list__section__container">
              <div class="line-up">
                <div class="invite-list__section__item">Has Products</div>
              </div>
              <div>
                <input type="checkbox" v-model="hasProducts" />
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

          <!-- <div>{{allForms}}</div> -->
          <div class="form__list">
            <div class="added-collection">
              <p class="added-collection__header">Users</p>
              <div class="added-collection__body">
                <Multiselect
                  placeholder="Select User"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                  v-model="selectedUsers"
                  :options="orgUsers"
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
                <button class="green_button" @click="openModal('user', selectedUsers)">Go</button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">Slack Form</p>
              <div class="added-collection__body">
                <Multiselect
                  placeholder="Select Slack Form"
                  style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                  v-model="selectedSlackForms"
                  :options="orgSlackForms"
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
                <button class="green_button" @click="openModal('slackForm', selectedSlackForms)">Go</button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">Slack Form Instances</p>
              <div class="added-collection__body">
                <button class="green_button" @click="goToSlackFormInstace()">Go</button>
              </div>
            </div>
            <div class="added-collection">
              <p class="added-collection__header">Meeting Workflows</p>
              <div class="added-collection__body">
                <button class="green_button" @click="goToMeetingWorkflow()">Go</button>
              </div>
            </div>
          </div>
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
          <h2>{{ selectedSlackForms.form_type }} {{ selectedSlackForms.resource }}</h2>
          <div v-for="(field, i) in selectedSlackForms.fields_ref" :key="field.field">
            <div style="margin-bottom: 1rem">
              {{ i + 1 }} | {{ field.field_ref.label }} ({{ field.field_ref.api_name }})
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'SlackFormInstance'">
        <button class="green_button back" @click="goBack">Back</button>
        <div
          :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'"
          v-for="(slackFormInstance, i) in orgSlackFormInstances"
          :key="slackFormInstance.id"
        >
          <h5 class="click click_width" @click="openModal('slackFormInstance', slackFormInstance)">
            {{ slackFormInstance.template_ref ? slackFormInstance.template_ref.resource : '-' }}
            {{ slackFormInstance.template_ref ? slackFormInstance.template_ref.form_type : '-' }} by
            {{ getUserName(slackFormInstance.user) }}
            {{
              slackFormInstance.submissionDate
                ? `at ${formatDateTime(slackFormInstance.submissionDate)} from ${
                    slackFormInstance.updateSource
                  }`
                : `(Not Submitted)`
            }}
          </h5>
        </div>
      </template>
      <template v-else-if="page === 'MeetingWorkflow'">
        <button class="green_button back" @click="goBack">Back</button>
        <div
          :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'"
          v-for="(meetingWorkflow, i) in orgMeetingWorkflows"
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
      <template v-else>
        <h2>Completed Tasks</h2>
        <div v-for="(task, i) in adminTasks" :key="task.pk">
          <div :class="i % 2 === 0 ? 'light-back padding' : 'pure-white padding'" @click="openModal('task', task)">
            <h4 class="click click_width">{{task.fields.task_name}} ({{formatDateTime(task.fields.run_at)}}, {{getTime(task.fields.run_at)}}) <span :style="task.fields.last_error ? 'color: red;' : 'color: green;'">{{task.fields.last_error ? '[ERROR]' : '[SUCCESS]'}}</span></h4>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'
import { MeetingWorkflows } from '@/services/salesforce'
import CollectionManager from '@/services/collectionManager'
import Organization from '@/services/organizations'
import User from '@/services/users'
import CustomSlackForm from '@/views/settings/CustomSlackForm'

export default {
  name: 'Staff',
  components: {
    CustomSlackForm,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      commandOptions: [
        { label: 'Salesforce Resources', value: 'SALESFORCE_RESOURCES' },
        { label: 'Salesforce Fields', value: 'SALESFORCE_FIELDS' },
        { label: 'Pull Usage Data', value: 'PULL_USAGE_DATA' },
      ],
      allUsers: CollectionManager.create({
        ModelClass: User,
      }),
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
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
      selectedUsers: null,
      selectedSlackForms: null,
      orgUsers: null,
      orgSlackForms: [],
      orgSlackFormInstances: null,
      selectedCommand: '',
      loading: true,
      editOpModalOpen: false,
      modalInfo: null,
      displayCommandModal: false,
      contentModalInfo: null,
      contentType: '',
      states: ['ACTIVE', 'INACTIVE'],
      stateActive: null,
      ignoreEmails: [],
      eventCalendarIDObj: {},
      fakeMeetingIDObj: {},
      zoomChannelObj: {},
      recapObj: {},
      realTimeAlertConfigObj: {},
      hasProducts: false,
      allForms: null,
      allMeetingWorkflows: null,
      orgMeetingWorkflows: null,
      selected_org: null,
      old_selected_org: null,
      slackFormInstances: null,
      adminTasks: null,
      modalName: '',
      page: null,
      orgForms: null,
      organizations: [],
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  mounted() {
    this.stateActive = this.user.organizationRef.state
    this.hasProducts = this.user.organizationRef.hasProducts
    this.ignoreEmails = this.user.organizationRef.ignoreEmailRef
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    getUserName(id) {
      const user = this.orgUsers.filter((user) => user.id == id)[0]
      return user ? `${user.firstName} ${user.lastName}` : '-'
    },
    clearUsersAndSlackForm() {
      this.selectedSlackForms = null
      this.selectedUsers = null
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm(null, true)
        this.allForms = res
      } catch (e) {
        console.log(e)
      }
    },
    async getAllMeetingWorkflows() {
      try {
        let res = await MeetingWorkflows.api.getMeetingList(true)
        this.allMeetingWorkflows = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async getTasks() {
      try {
        let res = await User.api.getTasks()
        const tasks = JSON.parse(res.tasks)
        this.adminTasks = tasks
      } catch(e) {
        console.log(e)
      }
    },
    async getStaffOrgs() {
      try {
        let res = await Organization.api.getStaffOrganizations()
        this.organizations = res
      } catch (e) {
        console.log(e)
      }
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
            console.log(res['message'])
            this.$toast('Something went wrong. Please try again.', {
              type: 'error',
              timeout: 3000,
            })
          }
        }
      } catch (e) {
        console.log(e)
        this.$toast('Something went wrong. Please try again.', {
          type: 'error',
          timeout: 3000,
        })
      }
    },
    async getSlackFormInstance() {
      try {
        const res = await SlackOAuth.api.slackFormInstances()
        this.slackFormInstances = res
      } catch (e) {
        console.log('Error in getSlackFormInstance', e)
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
        has_products: this.hasProducts,
        ignore_emails: noSpacesEmails,
        org_id: this.selected_org.id,
      }
      try {
        const res = await Organization.api.orgUpdate(orgUpdates)
        this.getStaffOrgs()
        this.$toast(
          'Organization Updated. Please wait a few seconds and then hard refresh (ctrl + shift + r)',
          {
            type: 'success',
            timeout: 4000,
          },
        )
      } catch (e) {
        console.log('error: ', e)
        this.$toast('Something went wrong.', {
          type: 'error',
          timeout: 3000,
        })
      }
    },
    async postUserInfo(index, userID) {
      const data = {
        event_calendar_id: this.eventCalendarIDObj[index],
        fake_meeting_id: this.fakeMeetingIDObj[index],
        zoom_channel: this.zoomChannelObj[index],
        recap_receivers: this.recapObj[index],
        realtime_alert_config: this.realTimeAlertConfigObj[index],
        user_id: userID,
      }
      const res = await User.api.usersUpdate(data).then(() => {
        this.allUsers.refresh()
      })
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
      return user.fullName.trim() ? user.fullName : user.email
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
    goToUser() {
      if (!this.selectedUsers || !this.selectedUsers.length) {
        return
      }
      this.selectedUsers.forEach((u, i) => {
        this.eventCalendarIDObj[i] = u.nylasRef.eventCalendarId
        this.fakeMeetingIDObj[i] = u.zoomRef.fakeMeetingIdRef
        this.zoomChannelObj[i] = u.slackAccount.zoomChannel
        this.recapObj[i] = u.slackAccount.recapReceivers
        // VV this is busted VV
        this.realTimeAlertConfigObj[i] = u.slackAccount.realtimeAlertConfigs.toString()
      })
      this.old_selected_org = this.selected_org
      this.selected_org = null
      this.page = 'Users'
    },
    goToSlackForm() {
      if (!this.selectedSlackForms) {
        return
      }
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
    openModal(name, data) {
      this.modalName = name
      this.modalInfo = data
      this.editOpModalOpen = true
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
      this.modalName = ''
      this.modalInfo = null
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
    filterUsers(org_id) {
      return this.allUsers.list.filter((user) => user.organization == org_id)
    },
  },
  created() {
    this.getTasks()
    this.getStaffOrgs()
    this.allUsers.refresh()
  },
  watch: {
    async organizations() {
      if (this.selected_org) {
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = await SlackOAuth.api.getStaffForms(this.selected_org.id)
        this.orgMeetingWorkflows = await MeetingWorkflows.api.getStaffMeetings(this.selected_org.id)
      }
    },
    async selected_org() {
      if (this.selected_org) {
        this.loading = false
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = await SlackOAuth.api.getStaffForms(this.selected_org.id)
        this.orgMeetingWorkflows = await MeetingWorkflows.api.getStaffMeetings(this.selected_org.id)
        this.orgSlackFormInstances = await SlackOAuth.api.getStaffFormInstances(
          this.selected_org.id,
        )
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
  height: 100vh;
}

.staff__drawer {
  width: 20vw;
  height: 40%;
  background-color: #fafbfc;
  border-right: 2px solid $soft-gray;
  border-bottom: 2px solid $soft-gray;
  padding-right: 1rem;
}

.staff__main_page {
  width: 70vw;
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
  width: 62vw;
}
ul {
  margin: 0;
  padding: 0;
}

.command_dropdown {
  display: flex;
}

.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: bold;
  font-size: 12px;
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
  min-height: 48vh;
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
.copy-margin {
  margin-right: 1rem;
}
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
    width: 62vw;
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
  width: 20%;
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
.bottom-margin {
  margin-bottom: 1rem;
}
</style>