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
        <div v-if="modalName === 'slackFormInstance'">
          <div class="modal-container__body">
            <!-- <div class="user_item_container">
              <div class="border-break">
                <h3>Resource ID:</h3>
                <h4>{{ modalInfo.resourceId ? modalInfo.resourceId : 'null' }}</h4>
              </div>
              <div class="border-break">
                <h3>Workflow:</h3>
                <h4>{{ modalInfo.workflowId ? modalInfo.workflowId : 'null' }}</h4>
              </div>
              <div class="border-break">
                <h3>Is Submitted:</h3>
                <h4>{{ modalInfo.submissionDate ? 'true' : 'false' }}</h4>
              </div>
              <div class="border-break">
                <h3>Submission Date:</h3>
                <h4>{{ modalInfo.submissionDate ? modalInfo.submissionDate : 'null' }}</h4>
              </div>
              <div class="border-break">
                <h3>Update Source:</h3>
                <h4>{{ modalInfo.updateSource ? modalInfo.updateSource : 'null' }}</h4>
              </div>
              <div class="border-break">
                <h3>User ID:</h3>
                <h4>{{ modalInfo.user }}</h4>
              </div>
              <div class="border-break">
                <h3>Template ID:</h3>
                <h4>{{ modalInfo.template }}</h4>
              </div>
              <div class="border-break">
                <h3>Saved Data:</h3>
                <h4>{{ modalInfo.savedData }}</h4>
              </div>
              <div class="border-break">
                <h3>Previous Data:</h3>
                <h4>{{ modalInfo.previousData }}</h4>
              </div>
            </div> -->
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>{{ modalInfo.templateRef.resource }} {{ modalInfo.templateRef.formType }} by {{ getUserName(modalInfo.user) }}</h4>
              </div>
            </div>
            <section class="note-section">
              <p class="note-section__title">
                Resource: {{modalInfo.resourceId ? modalInfo.resourceId : 'N/A'}}
              </p>
              <p class="note-section__date">
                {{modalInfo.submissionDate ? `Submitted on ${weekDay(modalInfo.submissionDate)} ${formatDateTime(modalInfo.submissionDate)}` : 'Not Submitted'}}
              </p>
              <p class="note-section__body">
                <span class="underline">Workflow ID:</span> {{ modalInfo.workflowId ? modalInfo.workflowId : 'null' }}
                <span class="underline">Update Source:</span> {{ modalInfo.updateSource ? modalInfo.updateSource : 'null' }}
                <span class="underline">User ID:</span> {{ modalInfo.user ? modalInfo.user : 'null' }}
                <span class="underline">Template ID:</span> {{ modalInfo.template ? modalInfo.template : 'null' }}
                <span class="underline">Saved Data:</span> {{ modalInfo.savedData ? modalInfo.savedData : 'null' }}
                <span class="underline">Previous Data:</span> {{ modalInfo.previousData ? modalInfo.previousData : 'null' }}
              </p>
            </section>
          </div>
        </div>
        <div v-else-if="modalName === 'meetingWorkflow'">
          <div class="modal-container__body">
            <!-- <h1 class="user_title">{{ modalInfo.meeting_ref.topic }}</h1>
            <div class="user_item_container">
              <div class="border-break tiny-spacing">
                <h3>Meeting ID:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.meeting_id ? modalInfo.meeting_ref.meeting_id : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Meeting UUID:</h3>
                <h4>
                  {{
                    modalInfo.meeting_ref.meeting_uuid ? modalInfo.meeting_ref.meeting_uuid : 'null'
                  }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Account ID:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.account_id ? modalInfo.meeting_ref.account_id : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Host ID:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.host_id ? modalInfo.meeting_ref.host_id : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Operator ID:</h3>
                <h4>
                  {{
                    modalInfo.meeting_ref.operator_id ? modalInfo.meeting_ref.operator_id : 'null'
                  }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Status:</h3>
                <h4>{{ modalInfo.meeting_ref.status ? modalInfo.meeting_ref.status : 'null' }}</h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Timezone:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.timezone ? modalInfo.meeting_ref.timezone : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Start Time:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.start_time ? modalInfo.meeting_ref.start_time : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>End Time:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.end_time ? modalInfo.meeting_ref.end_time : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Start URL:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.start_url ? modalInfo.meeting_ref.start_url : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Duration:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.duration ? modalInfo.meeting_ref.duration : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Original Duration:</h3>
                <h4>
                  {{
                    modalInfo.meeting_ref.original_duration
                      ? modalInfo.meeting_ref.original_duration
                      : 'null'
                  }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Total Minutes:</h3>
                <h4>
                  {{
                    modalInfo.meeting_ref.total_minutes
                      ? modalInfo.meeting_ref.total_minutes
                      : 'null'
                  }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Recurrence:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.recurrence ? modalInfo.meeting_ref.recurrence : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Join URL:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.join_url ? modalInfo.meeting_ref.join_url : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Operator:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.operator ? modalInfo.meeting_ref.operator : 'null' }}
                </h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Operation:</h3>
                <h4>
                  {{ modalInfo.meeting_ref.operation ? modalInfo.meeting_ref.operation : 'null' }}
                </h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Participants:</h3>
              <div v-if="modalInfo.meeting_ref.participants.length">
                <div
                  v-for="participant in modalInfo.meeting_ref.participants"
                  :key="participant.id"
                >
                  <div class="form_field tiny-spacing">
                    <h4 class="border-break">ID: {{ participant.id ? participant.id : 'null' }}</h4>
                    <h4 class="border-break">
                      Name:
                      {{
                        participant.secondary_data
                          ? `${participant.secondary_data.FirstName} ${participant.secondary_data.LastName}`
                          : 'null'
                      }}
                    </h4>
                    <h4 class="border-break">
                      Email: {{ participant.email ? participant.email : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      Owner: {{ participant.owner ? participant.owner : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      Account: {{ participant.account ? participant.account : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      External Owner:
                      {{ participant.external_owner ? participant.external_owner : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      External Account:
                      {{ participant.external_account ? participant.external_account : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      Imported By: {{ participant.imported_by ? participant.imported_by : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      Integration ID:
                      {{ participant.integration_id ? participant.integration_id : 'null' }}
                    </h4>
                    <h4 class="border-break">
                      Integration Source:
                      {{ participant.integration_source ? participant.integration_source : 'null' }}
                    </h4>
                  </div>
                </div>
              </div>
              <div v-else><h4 class="border-break tiny-spacing">null</h4></div>
            </div>
            <div class="user_item_container">
              <div class="border-break tiny-spacing">
                <h3>Type:</h3>
                <h4>{{ modalInfo.meeting_ref.type ? modalInfo.meeting_ref.type : 'null' }}</h4>
              </div>
              <div class="border-break tiny-spacing">
                <h3>Zoom Account:</h3>
                <h4>
                  {{
                    modalInfo.meeting_ref.zoom_account ? modalInfo.meeting_ref.zoom_account : 'null'
                  }}
                </h4>
              </div>
            </div> -->
            <div class="flex-row-spread sticky border-bottom">
              <div class="flex-row">
                <img src="@/assets/images/logo.png" class="logo" alt="" />
                <h4>{{ modalInfo.meeting_ref.topic }}</h4>
              </div>
            </div>
            <section class="note-section">
              <p class="note-section__title">
                Meeting ID: {{ modalInfo.meeting_ref.meeting_id ? modalInfo.meeting_ref.meeting_id : 'N/A' }}
              </p>
              <p class="note-section__date">
                Start Time: {{ modalInfo.meeting_ref.start_time ? `${weekDay(modalInfo.meeting_ref.start_time)} ${formatDateTime(modalInfo.meeting_ref.start_time)} at ${getTime(modalInfo.meeting_ref.start_time)}` : 'null' }}
              </p>
              <br>
              <p class="note-section__date">
                End Time: {{ modalInfo.meeting_ref.end_time ? `${weekDay(modalInfo.meeting_ref.end_time)} ${formatDateTime(modalInfo.meeting_ref.end_time)} at ${getTime(modalInfo.meeting_ref.end_time)}` : 'null' }}
              </p>
              <p class="note-section__body">
                <span class="underline">Meeting UUID:</span> {{ modalInfo.meeting_ref.meeting_uuid ? modalInfo.meeting_ref.meeting_uuid : 'null' }}
                <span class="underline">Account ID:</span> {{ modalInfo.meeting_ref.account_id ? modalInfo.meeting_ref.account_id : 'null' }}
                <span class="underline">Host ID:</span> {{ modalInfo.meeting_ref.host_id ? modalInfo.meeting_ref.host_id : 'null' }}
                <span class="underline">Operator ID:</span> {{ modalInfo.meeting_ref.operator_id ? modalInfo.meeting_ref.operator_id : 'null' }}
                <span class="underline">Status:</span> {{ modalInfo.meeting_ref.status ? modalInfo.meeting_ref.status : 'null' }}
                <span class="underline">Timezone:</span> {{ modalInfo.meeting_ref.timezone ? modalInfo.meeting_ref.timezone : 'null' }}
                <span class="underline">Start URL:</span> {{ modalInfo.meeting_ref.start_url ? modalInfo.meeting_ref.start_url : 'null' }}
                <span class="underline">Duration:</span> {{ modalInfo.meeting_ref.duration ? modalInfo.meeting_ref.duration : 'null' }}
                <span class="underline">Original Duration:</span> {{ modalInfo.meeting_ref.original_duration ? modalInfo.meeting_ref.original_duration : 'null' }}
                <span class="underline">Total Minutes:</span> {{ modalInfo.meeting_ref.total_minutes ? modalInfo.meeting_ref.total_minutes : 'null' }}
                <span class="underline">Recurrence:</span> {{ modalInfo.meeting_ref.recurrence ? modalInfo.meeting_ref.recurrence : 'null' }}
                <span class="underline">Join URL:</span> {{ modalInfo.meeting_ref.join_url ? modalInfo.meeting_ref.join_url : 'null' }}
                <span class="underline">Operator:</span> {{ modalInfo.meeting_ref.operator ? modalInfo.meeting_ref.operator : 'null' }}
                <span class="underline">Operation:</span> {{ modalInfo.meeting_ref.operation ? modalInfo.meeting_ref.operation : 'null' }}
                <span class="underline">Participants:</span> {{ modalInfo.meeting_ref.participants ? modalInfo.meeting_ref.participants : 'null' }}
                <span class="underline">Type:</span> {{ modalInfo.meeting_ref.type ? modalInfo.meeting_ref.type : 'null' }}
                <span class="underline">Zoom Account:</span> {{ modalInfo.meeting_ref.zoom_account ? modalInfo.meeting_ref.zoom_account : 'null' }}
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
          <div class="modal-container__body" v-for="(content, i) in contentModalInfo" :key="i">
            <div class="big_card_container">
              <div class="border-break">
                <h3>Date:</h3>
                <h4>{{ content.date }}</h4>
              </div>
              <div class="border-break">
                <h3>Users:</h3>
                <h4>{{ content.users }}</h4>
              </div>
              <div class="border-break">
                <h3>Workflows:</h3>
                <h4>{{ content.workflows }}</h4>
              </div>
              <div class="user_item_container">
                <div class="border-break">
                  <h3>Accounts Created:</h3>
                  <h4>{{ content.creates.accounts }}</h4>
                </div>
                <div class="border-break">
                  <h3>Contacts Created:</h3>
                  <h4>{{ content.creates.contacts }}</h4>
                </div>
                <div class="border-break">
                  <h3>Opportunities Created:</h3>
                  <h4>{{ content.creates.opportunities }}</h4>
                </div>
                <div class="border-break">
                  <h3>Products Created:</h3>
                  <h4>{{ content.creates.products }}</h4>
                </div>
                <div class="border-break">
                  <h3>Total Created:</h3>
                  <h4>{{ content.creates.total }}</h4>
                </div>
              </div>
              <div class="user_item_container">
                <div class="border-break">
                  <h3>Alert Updates:</h3>
                  <h4>{{ content.updates.alert }}</h4>
                </div>
                <div class="border-break">
                  <h3>Command Updates:</h3>
                  <h4>{{ content.updates.command }}</h4>
                </div>
                <div class="border-break">
                  <h3>Meeting Updates:</h3>
                  <h4>{{ content.updates.meeting }}</h4>
                </div>
                <div class="border-break">
                  <h3>Pipeline Updates:</h3>
                  <h4>{{ content.updates.pipeline }}</h4>
                </div>
                <div class="border-break">
                  <h3>Total Updates:</h3>
                  <h4>{{ content.updates.total }}</h4>
                </div>
              </div>
            </div>
          </div>
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
      <!-- <div :key="i" v-for="(org, i) in organizations.list">
        <div>{{org}}</div>
        <h2 @click="selected_org = org.id">{{ org.name }}</h2>
      </div> -->
      <h3 @click="test">Organizations</h3>
      <Multiselect
        placeholder="Select Organization"
        style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
        v-model="selected_org"
        :options="organizations.list"
        openDirection="below"
        selectLabel="Enter"
        track-by="value"
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
          <div style="border-bottom: 1px solid black; margin-left: 1rem">
            <!-- top bar here  -->
            <!-- {{selected_org}} -->
            <div>
              <div>State</div>
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
            <div>
              <div>Ignore Emails</div>
              <input
                class="wide"
                type="search"
                v-model="ignoreEmails"
                placeholder="Ignore Emails"
              />
            </div>
            <div>
              <div @click="test">Has Products</div>
              <input type="checkbox" v-model="hasProducts" />
            </div>
            <button style="margin-bottom: 1rem;" class="green_button" @click="postOrgUpdates()">Save Changes</button>
          </div>

          <!-- <div>{{allForms}}</div> -->
          <div class="form__list">
            <div class="form__list_item">
              <h3>Users</h3>
              <Multiselect
                placeholder="Select Users"
                style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                v-model="selectedUsers"
                :options="orgUsers"
                openDirection="below"
                selectLabel="Enter"
                track-by="id"
                label="fullName"
                :multiple="true"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
              </Multiselect>
              <button class="green_button" @click="goToUser(selectedUsers)">Go</button>
            </div>
            <div class="form__list_item">
              <h3>Slack Form</h3>
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
              <button class="green_button" @click="goToSlackForm()">Go</button>
            </div>
            <div class="form__list_item">
              <h3>Slack Form Instances</h3>
              <button class="green_button" @click="goToSlackFormInstace()">Go</button>
            </div>
            <div class="form__list_item">
              <h3>Meeting Workflows</h3>
              <button class="green_button" @click="goToMeetingWorkflow()">Go</button>
            </div>
          </div>
          <hr />
        </template>
      </template>
      <template v-else-if="page === 'Users'">
        <div v-for="(user, i) in selectedUsers" :key="user.id">
          <div>
            <button class="green_button back" @click="goBack">Back</button>
            <h2 class="user_title">User {{ i + 1 }}</h2>
          </div>
          <div class="big_card_container">
            <div class="user_item_container">
              <div class="border-break">
                <h3>First Name:</h3>
                <h4>{{ user.firstName }}</h4>
              </div>
              <div class="border-break">
                <h3>Last Name:</h3>
                <h4>{{ user.lastName }}</h4>
              </div>
              <div class="border-break">
                <h3>Email:</h3>
                <h4>{{ user.email }}</h4>
              </div>
              <div class="border-break">
                <h3>Is Active:</h3>
                <h4>{{ user.isActive }}</h4>
              </div>
              <div class="border-break">
                <h3>Is Invited:</h3>
                <h4>{{ user.isInvited }}</h4>
              </div>
              <div class="border-break">
                <h3>Is Admin:</h3>
                <h4>{{ user.isAdmin }}</h4>
              </div>
              <div class="border-break">
                <h3>Is Staff:</h3>
                <h4>{{ user.isStaff }}</h4>
              </div>
              <div class="border-break">
                <h3>User Level:</h3>
                <h4>{{ user.userLevel }}</h4>
              </div>
              <div class="border-break">
                <h3>Role:</h3>
                <h4>{{ user.role }}</h4>
              </div>
              <div class="border-break">
                <h3>Timezone:</h3>
                <h4>{{ user.timezone }}</h4>
              </div>
              <div class="border-break">
                <h3>Reminders:</h3>
                <!-- <h4>{{user.isInvited}}</h4> -->
                <h4>???</h4>
              </div>
              <div class="border-break">
                <h3>Activated Managr Configs:</h3>
                <h4>{{ user.activatedManagrConfigs }}</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h2>User Slack Integrations</h2>
              <div class="border-break">
                <h3>Slack ID:</h3>
                <h4>{{ user.slackRef.slackId }}</h4>
              </div>
              <div class="border-break">
                <h3>Channel:</h3>
                <h4>{{ user.slackAccount.channel }}</h4>
              </div>
              <div class="border-break">
                <h3>Organization Slack:</h3>
                <!-- VV This is clearly wrong. Figure out where list of these are VV -->
                <h4>{{ user.organizationRef.slackIntegration }}</h4>
              </div>
              <!-- <div class="border-break">
                <h3>Is Revoked:</h3>
                <h4>???</h4>
              </div> -->
              <div class="border-break">
                <h3>Is Onboarded:</h3>
                <h4>{{ user.onboarding }}</h4>
              </div>
              <div class="border-break">
                <h3>Zoom Channel:</h3>
                <div v-if="user.slackAccount.zoomChannel">
                  <h4>{{ user.slackAccount.zoomChannel }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Recap Channel:</h3>
                <div v-if="user.slackAccount.recapChannel">
                  <h4>{{ user.slackAccount.recapChannel }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Recap Recievers:</h3>
                <div v-if="user.slackAccount.recapReceivers.length">
                  <div v-for="receiver in user.slackAccount.recapReceivers" :key="receiver">
                    <h4>{{ user.receiver }}</h4>
                  </div>
                </div>
                <div v-else>null</div>
              </div>
              <!-- <div class="user_item_container">
                <h3>Recap Channel:</h3>
                <div v-if="user.slackAccount.realtimeAlertConfigs.length">
                  <h4>{{user.slackAccountrealtimeAlertConfigs}}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div> -->
            </div>
            <div class="user_item_container">
              <h2>Salesforce ({{ user.salesforceAccountRef.id }})</h2>
              <div class="border-break">
                <h3>SFDC ID:</h3>
                <div v-if="user.salesforceAccountRef.salesforceId">
                  <h4>{{ user.salesforceAccountRef.salesforceId }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>sobjects:</h3>
                <div v-if="user.salesforceAccountRef.sobjects">
                  <h4>{{ user.salesforceAccountRef.sobjects }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Instance URL:</h3>
                <div v-if="user.salesforceAccountRef.instanceUrl">
                  <h4>{{ user.salesforceAccountRef.instanceUrl }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Access Token:</h3>
                <div v-if="user.salesforceAccountRef.accessToken">
                  <h4>{{ user.salesforceAccountRef.accessToken }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
            </div>
            <div class="user_item_container">
              <h2>Nylas ({{ user.nylasRef.id }})</h2>
              <div class="border-break">
                <h3>Access Token:</h3>
                <div v-if="user.nylasRef.accessToken">
                  <h4>{{ user.nylasRef.accessToken }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Email:</h3>
                <div v-if="user.nylasRef.emailAddress">
                  <h4>{{ user.nylasRef.emailAddress }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Event Calendar ID:</h3>
                <div>
                  <input v-model="eventCalendarIDObj[i]">
                </div>
              </div>
              <div class="border-break">
                <h3>Provider:</h3>
                <div v-if="user.nylasRef.provider">
                  <h4>{{ user.nylasRef.provider }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
            </div>
            <div class="user_item_container">
              <h2>Zoom ({{ user.zoomRef.id }})</h2>
              <div class="border-break">
                <h3>Zoom ID:</h3>
                <div v-if="user.zoomRef.zoomId">
                  <h4>{{ user.zoomRef.zoomId }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Timezone:</h3>
                <div v-if="user.zoomRef.timezone">
                  <h4>{{ user.zoomRef.timezone }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Account ID:</h3>
                <div v-if="user.zoomRef.accountId">
                  <h4>{{ user.zoomRef.accountId }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Access Token:</h3>
                <div v-if="user.zoomRef.accessToken">
                  <h4>{{ user.zoomRef.accessToken }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Fake Meeting ID:</h3>
                <!-- <div v-if="user.zoomRef.fakeMeetingIdRef"> -->
                <div>
                  <!-- <h4>{{user.zoomRef.fakeMeetingIdRef}}</h4> -->
                  <input v-model="fakeMeetingIDObj[i]" />
                </div>
                <!-- <div v-else>
                  <h4>null</h4>
                </div> -->
              </div>
            </div>
            <div class="user_item_container">
              <h2>Slack Account ({{ user.slackAccount.slackId }})</h2>
              <div class="border-break">
                <h3>Slack ID:</h3>
                <div v-if="user.slackAccount.slackId">
                  <h4>{{ user.slackAccount.slackId }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Channel:</h3>
                <div v-if="user.slackAccount.channel">
                  <h4>{{ user.slackAccount.channel }}</h4>
                </div>
                <div v-else>
                  <h4>null</h4>
                </div>
              </div>
              <div class="border-break">
                <h3>Zoom Channel:</h3>
                <!-- <div v-if="user.slackAccount.zoomChannel"> -->
                <div>
                  <!-- <h4>{{user.slackAccount.zoomChannel}}</h4> -->
                  <input v-model="zoomChannelObj[i]" />
                </div>
                <!-- <div v-else>
                  <h4>null</h4>
                </div> -->
              </div>
              <div class="border-break">
                <h3>Recap Receivers:</h3>
                <!-- <div v-if="user.slackAccount.recapReceivers"> -->
                <div>
                  <!-- <h4>{{user.slackAccount.recapReceivers}}</h4> -->
                  <input v-model="recapObj[i]" />
                </div>
                <!-- <div v-else>
                  <h4>null</h4>
                </div> -->
              </div>
              <div class="border-break">
                <h3>Real Time Alert Configs:</h3>
                <!-- <div v-if="user.slackAccount.realtimeAlertConfigs"> -->
                <div>
                  <h4>{{ user.slackAccount.realtimeAlertConfigs }}</h4>
                  <!-- <input v-model="realTimeAlertConfigObj[i]"> -->
                </div>
                <!-- <div v-else>
                  <h4>null</h4>
                </div> -->
              </div>
            </div>
            <div>
              <button class="green_button" @click="postUserInfo(i, user.id)">Save Changes</button>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'SlackForm'">
        <button class="green_button back" @click="goBack">Back</button>
        <!-- <div v-for="(slackForm, i) in selectedSlackForms" :key="slackForm.id"> -->
        <div>
          <div>
            <h2 class="user_title">Slack Form</h2>
          </div>
          <!-- <h4>{{slackForm}}</h4> -->
          <div class="big_card_container">
            <div class="user_item_container">
              <div class="border-break">
                <h3>Form Type</h3>
                <h4>{{ selectedSlackForms.formType }}</h4>
              </div>
              <div class="border-break">
                <h3>Resource</h3>
                <h4>{{ selectedSlackForms.resource }}</h4>
              </div>
              <div class="border-break">
                <h3>Config</h3>
                <h4>>{{ selectedSlackForms.config }}</h4>
              </div>
              <div class="border-break">
                <h3>Stage</h3>
                <h4>{{ selectedSlackForms.stage ? slackForm.stage : 'null' }}</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Form Fields</h3>
              <div v-for="fieldRef in selectedSlackForms.fieldsRef" :key="fieldRef.id">
                <!-- <h3>Label: {{fieldRef.label}}</h3>
                <h3>Order: {{fieldRef.order}}</h3> -->
                <div class="form_field">
                  <div class="form_field_item border-break">
                    <h3>Field:</h3>
                    <h4>{{ fieldRef.referenceDisplayLabel }}</h4>
                  </div>
                  <div class="form_field_item border-break">
                    <h3>Order:</h3>
                    <h4>{{ fieldRef.order }}</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'SlackFormInstance'">
        <button class="green_button back" @click="goBack">Back</button>
        <div :class="i % 2 === 0 ? 'padding' : 'light-back padding'" v-for="(slackFormInstance, i) in slackFormInstances" :key="slackFormInstance.id">
          <h3
            class='click click_width'
            @click="openModal('slackFormInstance', slackFormInstance)"
          >
            {{ slackFormInstance.templateRef.resource }} {{ slackFormInstance.templateRef.formType }} by {{ getUserName(slackFormInstance.user) }}
          </h3>
        </div>
      </template>
      <template v-else-if="page === 'MeetingWorkflow'">
        <button class="green_button back" @click="goBack">Back</button>
        <div :class="i % 2 === 0 ? 'padding' : 'light-back padding'" v-for="(meetingWorkflow, i) in orgMeetingWorkflows" :key="meetingWorkflow.id">
          <h3
            class='click click_width'
            @click="openModal('meetingWorkflow', meetingWorkflow)"
          >
            {{ meetingWorkflow.meeting_ref.topic }}
          </h3>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'
import { SObjects, SObjectPicklist, MeetingWorkflows } from '@/services/salesforce'
import CollectionManager from '@/services/collectionManager'
import Organization from '@/services/organizations'
import COMMANDS from './staff-constants'
import User from '@/services/users'

export default {
  name: 'Staff',
  components: {
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
      selectedUsers: null,
      selectedSlackForms: null,
      orgUsers: null,
      orgSlackForms: null,
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
      selected_org: null,
      old_selected_org: null,
      slackFormInstances: null,
      modalName: '',
      page: null,
      orgForms: null,
      orgMeetingWorkflows: null,
      organizations: CollectionManager.create({ ModelClass: Organization }),
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
    test() {
      console.log('test', this.eventCalendarIDObj)
    },
    getUserName(id) {
      const user = this.orgUsers.filter((user) => user.id == id)[0]
      return `${user.firstName} ${user.lastName}`
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.allForms = res
      } catch (e) {
        console.log(e)
      }
    },
    async getAllMeetingWorkflows() {
      try {
        let res = await MeetingWorkflows.api.getMeetingList()
        this.allMeetingWorkflows = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async runCommand() {
      if (!this.selectedCommand || !this.selectedCommand.value) {
        this.$Alert.alert({
          type: 'failure',
          timeout: 4000,
          message: 'Please select a command.',
        })
        return
      }
      try {
        const res = await User.api.callCommand(this.selectedCommand.value).then((res) => {
          if (res.data) {
            const newResContent = []
            for (let key in res.data) {
              const item = res.data[key]
              item['date'] = key
              newResContent.push(item)
            }
            this.contentModalInfo = newResContent
            this.displayCommandModal = true
            this.contentType = 'PullUsageData'
          } else {
            this.$Alert.alert({
              type: 'success',
              timeout: 4000,
              message: res['message'],
            })
          }
        })
      } catch (e) {
        console.log(e)
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
        const refresh = await this.organizations.refresh()
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message:
            'Organization Updated. Please wait a few seconds and then hard refresh (ctrl + shift + r)',
        })
      } catch (e) {
        console.log('error: ', e)
        this.$Alert.alert({
          type: 'failure',
          timeout: 4000,
          message: 'Something went wrong. Check the console for full error report.',
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
    getTime(input) {
      let newer = new Date(input)
      console.log(`Time: ${newer.getHours()}:${newer.getMinutes()}`)
      let hours = newer.getHours();
      let minutes = newer.getMinutes();
      let afternoon = false;
      if (hours === 0) {
        hours = 12;
      }
      else if (hours === 12) {
        afternoon = true;
      }
      else if (hours > 12) {
        hours = hours - 12;
        afternoon = true
      }
      if (afternoon) {
        return `${hours}:${minutes} PM`
      } else {
        return `${hours}:${minutes} AM`
      }
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
      this.getSlackFormInstance()
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
    slackFormLabel({ formType, resource }) {
      let formattedFormType = formType[0]
      for (let i = 1; i < formType.length; i++) {
        formattedFormType += formType[i].toLowerCase()
      }
      return `${formattedFormType} ${resource}`
    },
    filterOrgForms(org_id) {
      return this.allForms.filter((form) => form.organization == org_id)
    },
    filterMeetingWorkflow(org_id) {
      return this.allMeetingWorkflows.filter((workflow) => workflow.org_ref.id == org_id)
    },
    showOrgData(org_id) {
      this.orgForms = this.filterOrgForms(org_id)
      this.orgMeetingWorkflows = this.filterMeetingWorkflow(org_id)
    },
    filterUsers(org_id) {
      return this.allUsers.list.filter((user) => user.organization == org_id)
    },
    filterSlackForms(org_id) {
      return this.allForms.filter((form) => form.organization == org_id)
    },
  },
  created() {
    this.getAllForms()
    this.getAllMeetingWorkflows()
    this.organizations.refresh()
    this.allUsers.refresh()
  },
  watch: {
    organizations() {
      if (this.selected_org) {
        this.selected_org.id = this.organizations[0].id
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = this.filterSlackForms(this.selected_org.id)
        this.orgMeetingWorkflows = this.filterMeetingWorkflow(this.selected_org.id)
      }
    },
    selected_org() {
      if (this.selected_org) {
        this.showOrgData(this.selected_org.id)
        this.loading = false
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = this.filterSlackForms(this.selected_org.id)
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
  border-right: 1px solid black;
}

.staff__main_page {
  width: 70vw;
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
  flex-wrap: wrap;
}
ul {
  margin: 0;
  padding: 0;
}
.form__list_item {
  padding: 0 2rem 2rem 2rem;
  border: 1px solid black;
  border-radius: 0.4rem;
  width: 30vw;
  margin: 1rem;
}
.sub_text {
  font-size: 12px;
  padding-left: 1rem;
}

.field__list_item {
  display: flex;
  flex-direction: column;
}

.command_dropdown {
  // margin: 2rem;
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
  border: none;
  background-color: white;
  padding: 4px;
  margin: 0;
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
.user_title {
  margin-left: 1rem;
}
.user_item_container {
  border: 1px solid black;
  margin: 1rem;
  padding: 0.25rem 1rem;
  border-radius: 0.4rem;

  h3 {
    margin: 0;
  }

  h4 {
    margin: 0.25rem 0.5rem;
    overflow-wrap: break-word;
  }
}
.form_field {
  border: 1px dashed black;
  border-radius: 0.4rem;
  margin: 1rem 0;
  padding: 0.25rem 1rem;
}
.form_field_item {
  margin: 0.5rem 0;

  h3 {
    margin: 0;
  }

  h4 {
    margin: 0.25rem 0.5rem;
    overflow-wrap: break-word;
  }
}
.back {
  margin: 1rem;
  text-decoration: underline;
  cursor: pointer;
}
.modal-container {
  background-color: $white;
  overflow: auto;
  width: 44vw;
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
  &__footer {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    position: sticky;
    height: 8vh;
    padding: 0.5rem;
  }
}

.email_text_container {
  display: flex;
  div {
    margin: 0.5rem 0.5rem 0.5rem 0;
  }
}
.removed_email {
  text-decoration: line-through;
  color: $very-light-gray;
}
.light-back {
  background-color: $white-green;
}
.big_card_container {
  border: 1px solid black;
  border-radius: 0.4rem;
  box-shadow: 1px 1px 3px black;
  margin: 1rem;
  padding: 0.25rem;
}
.border-break {
  border-bottom: 1px solid $very-light-gray;
}
.tiny-spacing {
  h3 {
    margin: 0.25rem 0;
  }
  h4 {
    margin: 0.25rem 0;
  }
}
.click {
  cursor: pointer;
}
.click_width {
  width: max-content;
}
.padding {
  padding: .5rem 1rem;
}
.rel {
  position: relative;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
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
.note-border {
  border: 1px solid $very-light-gray;
  border-radius: 6px;
  padding: 4px;
  margin: 0px 6px;
  font-size: 12px;
}
.light-green-bg {
  background-color: $white-green;
  color: $dark-green !important;
  border: 1px solid $dark-green !important;
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
}
</style>