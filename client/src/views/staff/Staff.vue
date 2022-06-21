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
            <!-- {{modalInfo}} -->
            <div>
              <h3>Resource ID:</h3>
              <h4>{{modalInfo.resource_id ? modalInfo.resource_id : 'null'}}</h4>
            </div>
            <div>
              <h3>Workflow:</h3>
              <h4>{{modalInfo.workflow_id ? modalInfo.workflow_id : 'null'}}</h4>
            </div>
            <div>
              <h3>Is Submitted:</h3>
              <h4>{{modalInfo.submission_date ? "true" : "false"}}</h4>
            </div>
            <div>
              <h3>Submission Date:</h3>
              <h4>{{modalInfo.submission_date ? modalInfo.submission_date : "null"}}</h4>
            </div>
            <div>
              <h3>Update Source:</h3>
              <h4>{{modalInfo.update_source ? modalInfo.update_source : 'null'}}</h4>
            </div>
            <div>
              <h3>User ID:</h3>
              <h4>{{modalInfo.user_id}}</h4>
            </div>
            <div>
              <h3>Template ID:</h3>
              <h4>{{modalInfo.template_id}}</h4>
            </div>
            <div>
              <h3>Saved Data:</h3>
              <h4>{{modalInfo.saved_data}}</h4>
            </div>
            <div>
              <h3>Previous Data:</h3>
              <h4>{{modalInfo.previous_data}}</h4>
            </div>
            <div>
              <h3>Alert Instance ID:</h3>
              <h4>{{modalInfo.alert_instance_id_id ? modalInfo.alert_instance_id_id : 'null'}}</h4>
            </div>
          </div>
        </div>
        <div v-else-if="modalName === 'meetingWorkflow'">
          <div class="modal-container__body">
            <!-- {{modalInfo}} -->
            <div>
              <h3>Meeting ID:</h3>
              <h4>{{modalInfo.meeting_ref.meeting_id ? modalInfo.meeting_ref.meeting_id : 'null'}}</h4>
            </div>
            <div>
              <h3>Meeting UUID:</h3>
              <h4>{{modalInfo.meeting_ref.meeting_uuid ? modalInfo.meeting_ref.meeting_uuid : 'null'}}</h4>
            </div>
            <div>
              <h3>Account ID:</h3>
              <h4>{{modalInfo.meeting_ref.account_id ? modalInfo.meeting_ref.account_id : 'null'}}</h4>
            </div>
            <div>
              <h3>Host ID:</h3>
              <h4>{{modalInfo.meeting_ref.host_id ? modalInfo.meeting_ref.host_id : 'null'}}</h4>
            </div>
            <div>
              <h3>Operator ID:</h3>
              <h4>{{modalInfo.meeting_ref.operator_id ? modalInfo.meeting_ref.operator_id : 'null'}}</h4>
            </div>
            <div>
              <h3>Status:</h3>
              <h4>{{modalInfo.meeting_ref.status ? modalInfo.meeting_ref.status : 'null'}}</h4>
            </div>
            <div>
              <h3>Timezone:</h3>
              <h4>{{modalInfo.meeting_ref.timezone ? modalInfo.meeting_ref.timezone : 'null'}}</h4>
            </div>
            <div>
              <h3>Start Time:</h3>
              <h4>{{modalInfo.meeting_ref.start_time ? modalInfo.meeting_ref.start_time : 'null'}}</h4>
            </div>
            <div>
              <h3>End Time:</h3>
              <h4>{{modalInfo.meeting_ref.end_time ? modalInfo.meeting_ref.end_time : 'null'}}</h4>
            </div>
            <div>
              <h3>Start URL:</h3>
              <h4>{{modalInfo.meeting_ref.start_url ? modalInfo.meeting_ref.start_url : 'null'}}</h4>
            </div>
            <div>
              <h3>Duration:</h3>
              <h4>{{modalInfo.meeting_ref.duration ? modalInfo.meeting_ref.duration : 'null'}}</h4>
            </div>
            <div>
              <h3>Original Duration:</h3>
              <h4>{{modalInfo.meeting_ref.original_duration ? modalInfo.meeting_ref.original_duration : 'null'}}</h4>
            </div>
            <div>
              <h3>Total Minutes:</h3>
              <h4>{{modalInfo.meeting_ref.total_minutes ? modalInfo.meeting_ref.total_minutes : 'null'}}</h4>
            </div>
            <div>
              <h3>Recurrence:</h3>
              <h4>{{modalInfo.meeting_ref.recurrence ? modalInfo.meeting_ref.recurrence : 'null'}}</h4>
            </div>
            <div>
              <h3>Join URL:</h3>
              <h4>{{modalInfo.meeting_ref.join_url ? modalInfo.meeting_ref.join_url : 'null'}}</h4>
            </div>
            <div>
              <h3>Operator:</h3>
              <h4>{{modalInfo.meeting_ref.operator ? modalInfo.meeting_ref.operator : 'null'}}</h4>
            </div>
            <div>
              <h3>Operation:</h3>
              <h4>{{modalInfo.meeting_ref.operation ? modalInfo.meeting_ref.operation : 'null'}}</h4>
            </div>
            <div>
              <h3>Participants:</h3>
              <div v-if="modalInfo.meeting_ref.participants.length">
                <div v-for="participant in modalInfo.meeting_ref.participants" :key="participant.id">
                  <h4>ID: {{participant.id ? participant.id : 'null'}}</h4>
                  <h4>Name: {{participant.secondary_data ? `${participant.secondary_data.FirstName} ${participant.secondary_data.LastName}` : 'null'}}</h4>
                  <h4>Email: {{participant.email ? participant.email : 'null'}}</h4>
                  <h4>Owner: {{participant.owner ? participant.owner : 'null'}}</h4>
                  <h4>Account: {{participant.account ? participant.account : 'null'}}</h4>
                  <h4>External Owner: {{participant.external_owner ? participant.external_owner : 'null'}}</h4>
                  <h4>External Account: {{participant.external_account ? participant.external_account : 'null'}}</h4>
                  <h4>Imported By: {{participant.imported_by ? participant.imported_by : 'null'}}</h4>
                  <h4>Integration ID: {{participant.integration_id ? participant.integration_id : 'null'}}</h4>
                  <h4>Integration Source: {{participant.integration_source ? participant.integration_source : 'null'}}</h4>
                </div>
              </div>
              <div v-else><h4>null</h4></div>
              <!-- <h4>{{modalInfo.meeting_ref.participants ? modalInfo.meeting_ref.participants : 'null'}}</h4> -->
            </div>
            <div>
              <h3>Type:</h3>
              <h4>{{modalInfo.meeting_ref.type ? modalInfo.meeting_ref.type : 'null'}}</h4>
            </div>
            <div>
              <h3>Zoom Account:</h3>
              <h4>{{modalInfo.meeting_ref.zoom_account ? modalInfo.meeting_ref.zoom_account : 'null'}}</h4>
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
                v-model="ignoreEmailText" 
                placeholder="Ignore Emails" 
                @keyup.enter="ignoreEmail"
              />
              <!-- <p>{{ignoreEmailText}}</p> -->
              <div v-for="email in ignoreEmails" :key="email">
                <div v-if="!newIgnoreEmails.includes(email)" class="email_text_container">
                  <div class="removed_email">{{email}}</div>
                </div>
                <div v-else class="email_text_container">
                  <div>{{email}}</div>
                  <div @click="removeEmail(email)" style="cursor: pointer;">X</div>
                </div>
              </div>
            </div>
            <div>
              <div @click="test">Has Products</div>
              <input 
                type="checkbox" 
                v-model="hasProducts" 
              />
            </div>
            <button class="green_button" @click="postOrgUpdates({ignore_emails: newIgnoreEmails, has_products: hasProducts, state_active: stateActive, org_id: selected_org ? selected_org.id : old_selected_org.id})">Save Changes</button>
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
                :multiple="true"
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
          <div class="form__List">
            <div :key="i" class="field__list_item" v-for="(workflow, i) in orgMeetingWorkflows">
              <h4>
                {{ 'event_data' in workflow.meeting_ref ? 'Google Meet' : 'Zoom Meeting' }} --
                {{
                  'event_data' in workflow.meeting_ref
                    ? workflow.meeting_ref['event_data']['title']
                    : workflow.meeting_ref.topic
                }}
              </h4>
              <ul>
                <li
                  v-for="(participant, index) in workflow.meeting_ref.participants"
                  :key="participant['email']"
                >
                  {{ participant['email'] }}
                </li>
              </ul>
            </div>
          </div>
        </template>
      </template>
      <template v-else-if="page === 'Users'">
        <div v-for="(user, i) in selectedUsers" :key="user.id">
          <div>
            <button class="green_button back" @click="goBack">Back</button>
            <h2 class="user_title">User {{i + 1}}</h2>
          </div>
          <div class="user_item_container">
            <h3>First Name:</h3>
            <h4>{{user.firstName}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Last Name:</h3>
            <h4>{{user.lastName}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Email:</h3>
            <h4>{{user.email}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Active:</h3>
            <h4>{{user.isActive}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Invited:</h3>
            <h4>{{user.isInvited}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Admin:</h3>
            <h4>{{user.isAdmin}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Staff:</h3>
            <h4>{{user.isStaff}}</h4>
          </div>
          <div class="user_item_container">
            <h3>User Level:</h3>
            <h4>{{user.userLevel}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Role:</h3>
            <h4>{{user.role}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Timezone:</h3>
            <h4>{{user.timezone}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Reminders:</h3>
            <!-- <h4>{{user.isInvited}}</h4> -->
            <h4>???</h4>
          </div>
          <div class="user_item_container">
            <h3>Activated Managr Configs:</h3>
            <h4>{{user.activatedManagrConfigs}}</h4>
          </div>
          <div>
            <h2>User Slack Integrations</h2>
            <div class="user_item_container">
              <h3>Slack ID:</h3>
              <h4>{{user.slackRef.slackId}}</h4>
            </div>
            <div class="user_item_container">
              <h3>Channel:</h3>
              <h4>{{user.slackAccount.channel}}</h4>
            </div>
            <div class="user_item_container">
              <h3>Organization Slack:</h3>
              <!-- VV This is clearly wrong. Figure out where list of these are VV -->
              <h4>{{user.organizationRef.slackIntegration}}</h4>
            </div>
            <!-- <div class="user_item_container">
              <h3>Is Revoked:</h3>
              <h4>???</h4>
            </div> -->
            <div class="user_item_container">
              <h3>Is Onboarded:</h3>
              <h4>{{user.onboarding}}</h4>
            </div>
            <div class="user_item_container">
              <h3>Zoom Channel:</h3>
              <div v-if="user.slackAccount.zoomChannel">
                <h4>{{user.slackAccount.zoomChannel}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Recap Channel:</h3>
              <div v-if="user.slackAccount.recapChannel">
                <h4>{{user.slackAccount.recapChannel}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Recap Recievers:</h3>
              <div v-if="user.slackAccount.recapReceivers.length">
                <div v-for="(receiver) in user.slackAccount.recapReceivers" :key="receiver">
                  <h4>{{user.receiver}}</h4>
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
          <div>
            <h2>Salesforce ({{user.salesforceAccountRef.id}})</h2>
            <div class="user_item_container">
              <h3>SFDC ID:</h3>
              <div v-if="user.salesforceAccountRef.salesforceId">
                <h4>{{user.salesforceAccountRef.salesforceId}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>sobjects:</h3>
              <div v-if="user.salesforceAccountRef.sobjects">
                <h4>{{user.salesforceAccountRef.sobjects}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Instance URL:</h3>
              <div v-if="user.salesforceAccountRef.instanceUrl">
                <h4>{{user.salesforceAccountRef.instanceUrl}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Access Token:</h3>
              <div v-if="user.salesforceAccountRef.accessToken">
                <h4>{{user.salesforceAccountRef.accessToken}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
          </div>
          <div>
            <h2>Nylas ({{user.nylasRef.id}})</h2>
            <div class="user_item_container">
              <h3>Access Token:</h3>
              <div v-if="user.nylasRef.accessToken">
                <h4>{{user.nylasRef.accessToken}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Email:</h3>
              <div v-if="user.nylasRef.emailAddress">
                <h4>{{user.nylasRef.emailAddress}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Event Calendar ID:</h3>
              <div v-if="user.nylasRef.eventCalendarId">
                <!-- Value will be eventCalendarIDVal[i] -->
                <!-- eventCalendarIDVal will be assigned when selected users are assigned -->
                <!-- For every user, push in an array that is user.nylasRef.eventCalendarId -->
                <!-- Set up object with i as key and eventCalendarIDVal[i] as value -->
                <!-- On change, change the key of i to value of input -->
                <input v-model="eventCalendarIDObj[i]">
              </div>
              <!-- <div v-else>
                <input>null</input>
              </div> -->
            </div>
            <div class="user_item_container">
              <h3>Provider:</h3>
              <div v-if="user.nylasRef.provider">
                <h4>{{user.nylasRef.provider}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
          </div>
          <div>
            <h2>Zoom ({{user.zoomRef.id}})</h2>
            <div class="user_item_container">
              <h3>Zoom ID:</h3>
              <div v-if="user.zoomRef.zoomId">
                <h4>{{user.zoomRef.zoomId}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Timezone:</h3>
              <div v-if="user.zoomRef.timezone">
                <h4>{{user.zoomRef.timezone}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Account ID:</h3>
              <div v-if="user.zoomRef.accountId">
                <h4>{{user.zoomRef.accountId}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Access Token:</h3>
              <div v-if="user.zoomRef.accessToken">
                <h4>{{user.zoomRef.accessToken}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Fake Meeting ID:</h3>
              <div v-if="user.zoomRef.fakeMeetingIdRef">
                <h4>{{user.zoomRef.fakeMeetingIdRef}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
          </div>
          <div>
            <h2>Slack Account ({{user.slackAccount.slackId}})</h2>
            <div class="user_item_container">
              <h3>Slack ID:</h3>
              <div v-if="user.slackAccount.slackId">
                <h4>{{user.slackAccount.slackId}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Channel:</h3>
              <div v-if="user.slackAccount.channel">
                <h4>{{user.slackAccount.channel}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Zoom Channel:</h3>
              <div v-if="user.slackAccount.zoomChannel">
                <h4>{{user.slackAccount.zoomChannel}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Recap Receivers:</h3>
              <div v-if="user.slackAccount.recapReceivers">
                <h4>{{user.slackAccount.recapReceivers}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
            <div class="user_item_container">
              <h3>Real Time Alert Configs:</h3>
              <div v-if="user.slackAccount.realtimeAlertConfigs">
                <h4>{{user.slackAccount.realtimeAlertConfigs}}</h4>
              </div>
              <div v-else>
                <h4>null</h4>
              </div>
            </div>
          </div>
          <!-- <div>
            <div class="user_item_container">
              <h3>Zoom ID:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Email:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Type:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Role Name:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Timezone:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Host Key:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Account ID:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Language:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Status:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Access Token:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Refresh Token:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Token Generated Date:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Token Scope:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Is Revoked:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Refresh Token Task:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Fake Meeting ID:</h3>
              <h4>???</h4>
            </div>
          </div>
          <div>
            <div class="user_item_container">
              <h3>Auth Account:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Salesloft ID:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Guid:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Is Active:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Email:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Team ID:</h3>
              <h4>???</h4>
            </div>
          </div> -->
        </div>
      </template>
      <template v-else-if="page === 'SlackForm'">
        <div v-for="(slackForm, i) in selectedSlackForms" :key="slackForm.id">
          <div>
            <button class="green_button back" @click="goBack">Back</button>
            <h2 class="user_title">Slack Form {{i + 1}}</h2>
          </div>
          <!-- <h4>{{slackForm}}</h4> -->
          <div>
            <div class="user_item_container">
              <h3>Organization</h3>
              <!-- <h4>{{old_selected_org.name}}</h4> -->
            </div>
            <div class="user_item_container">
              <h3>Form Type</h3>
              <h4>{{slackForm.formType}}</h4>
            </div>
            <div class="user_item_container">
              <h3>Resource</h3>
              <h4>{{slackForm.resource}}</h4>
            </div>
            <div class="user_item_container">
              <h3>Config</h3>
              <h4>>{{slackForm.config}}</h4>
            </div>
            <div class="user_item_container">
              <h3>Stage</h3>
              <h4>{{slackForm.stage ? slackForm.stage : 'null'}}</h4>
            </div>
          </div>
          <div>
            <h3>Form Fields</h3>
            <div v-for="(fieldRef) in slackForm.fieldsRef" :key="fieldRef.id">
              <!-- <h3>Label: {{fieldRef.label}}</h3>
              <h3>Order: {{fieldRef.order}}</h3> -->
              <div class="user_item_container">
                <h3>Field</h3>
                <h4>{{fieldRef.referenceDisplayLabel}}</h4>
              </div>
              <div class="user_item_container">
                <h3>Order</h3>
                <h4>{{fieldRef.order}}</h4>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'SlackFormInstance'">
        <button class="green_button back" @click="goBack">Back</button>
        <div v-for="(slackFormInstance, i) in slackFormInstances" :key="slackFormInstance.id">
          <h3 @click="openModal('slackFormInstance', slackFormInstance)">{{slackFormInstance.id}}</h3>
          <!-- <div>
            <h3>Resource ID:</h3>
            <h4>{{slackFormInstance.resource_id}}</h4>
          </div> -->
        </div>
      </template>
      <template v-else-if="page === 'MeetingWorkflow'">
        <!-- <div>{{orgMeetingWorkflows[0]}}</div> -->
        <button class="green_button back" @click="goBack">Back</button>
        <div v-for="(meetingWorkflow) in orgMeetingWorkflows" :key="meetingWorkflow.id">
          <h3 @click="openModal('meetingWorkflow', meetingWorkflow)">{{meetingWorkflow.meeting_ref.topic}}</h3>
          <!-- <h3>Full Name: {{slackForm.fullName}}</h3> -->
          <!-- <h3>Email: {{slackForm.email}}</h3> -->
          <!-- <h3>Role: {{slackForm.role}}</h3> -->
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
      ],
      allUsers: CollectionManager.create({
        ModelClass: User,
      }),
      selectedUsers: null,
      selectedSlackForms: null,
      orgUsers: null,
      orgSlackForms: null,
      selectedCommand: '',
      loading: true,
      editOpModalOpen: false,
      modalInfo: null,
      states: ['ACTIVE', 'INACTIVE'],
      stateActive: null, // change to whatever info is coming in
      ignoreEmailText: '',
      ignoreEmails: [], // change to whatever info is coming in
      newIgnoreEmails: [],
      eventCalendarIDObj: {},
      hasProducts: false, // change to whatever info is coming in
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
    this.stateActive = this.user.organizationRef.state;
    this.hasProducts = this.user.organizationRef.hasProducts;
    this.ignoreEmails = this.user.organizationRef.ignoreEmailRef;
    this.newIgnoreEmails = this.ignoreEmails;
    console.log('this.stateActive', this.user)
  },
  methods: {
    test() {
      console.log('test', this.eventCalendarIDObj)
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.allForms = res
        console.log('getAllForms', this.allForms[0])
      } catch (e) {
        console.log(e)
      }
    },
    async getAllMeetingWorkflows() {
      try {
        let res = await MeetingWorkflows.api.getMeetingList()
        console.log('res.results', res.results)
        this.allMeetingWorkflows = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async runCommand() {
      try {
        const res = await User.api.callCommand(this.selectedCommand.value).then((res) => {
          this.$Alert.alert({
            type: 'success',
            timeout: 4000,
            message: res['message'],
          })
        })
      } catch (e) {
        console.log(e)
      }
    },
    async getSlackFormInstance() {
      try {
        const res = await SlackOAuth.api.slackInstances(this.selected_org.id)
        console.log('slackFormInstanceRes', res)
        // User.api.getUser(this.user.id).then((response) => {
          //   this.$store.commit('UPDATE_USER', response)
          // })
        this.slackFormInstances = res;
      } catch(e) {
        console.log('Error in getSlackFormInstance', e)
      }
    },
    async postOrgUpdates(data) {
      console.log(data)
      const res = await Organization.api.orgUpdate(data).then(() => {
        this.organizations.refresh();
      });
      // console.log('res!!!', res)
    },
    ignoreEmail() {
      if (!this.checkEmail()) {
        return console.log('Please enter a valid email')
      }
      this.ignoreEmails.push(this.ignoreEmailText);
      this.newIgnoreEmails.push(this.ignoreEmailText);
      this.ignoreEmailText = '';
      console.log('ignoreEmails', this.newIgnoreEmails, Array.isArray(this.ignoreEmails));
    },
    checkEmail() {
      let symbol = false;
      let dot = false;
      if (this.ignoreEmailText[0] === '.' || this.ignoreEmailText[0] === '@') {
        return false;
      }
      for (let i = 0; i < this.ignoreEmailText.length; i++) {
        if (!symbol) {
          if (this.ignoreEmailText[i] === '@') {
            if (this.ignoreEmailText[i+1] === '.' || this.ignoreEmailText[i-1] === '.') {
              return false;
            }
            symbol = true;
          }
        } else if (!dot) {
          if (this.ignoreEmailText[i] === '.') {
            dot = true;
          }
        } else {
          return true;
        }
      }
      return false;
    },
    removeEmail(email) {
      this.newIgnoreEmails = this.newIgnoreEmails.filter(em => em !== email)
    },
    goBack() {
      this.selected_org = this.old_selected_org;
      this.old_selected_org = null;
      this.page = null;
    },
    goToUser() {
      if (!this.selectedUsers || !this.selectedUsers.length) {
        return;
      }
      this.selectedUsers.forEach((u, i) => this.eventCalendarIDObj[i] = u.nylasRef.eventCalendarId)
      console.log('this.eventCalendarIDObj', this.eventCalendarIDObj)
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'Users';
    },
    goToSlackForm() {
      if (!this.selectedSlackForms || !this.selectedSlackForms.length) {
        return;
      }
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'SlackForm';
      console.log('selectedSlackForms', this.selectedSlackForms)
    },
    goToSlackFormInstace() {
      this.getSlackFormInstance()
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'SlackFormInstance';
    },
    goToMeetingWorkflow() {
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'MeetingWorkflow';
    },
    openModal(name, data) {
      this.modalName = name;
      this.modalInfo = data;
      console.log('modal data', data)
      this.editOpModalOpen = true;
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen;
      this.modalName = '';
      this.modalInfo = null;
    },
    slackFormLabel({formType, resource}) {
      let formattedFormType = formType[0];
      for (let i = 1; i < formType.length; i++) {
        formattedFormType += formType[i].toLowerCase();
      }
      return `${formattedFormType} ${resource}`;
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
        // console.log('this.orgSlackForms', this.orgSlackForms)
      }
    },
    selected_org() {
      if (this.selected_org) {
        this.showOrgData(this.selected_org.id)
        this.loading = false
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = this.filterSlackForms(this.selected_org.id)
        console.log('this.orgSlackForms', this.orgSlackForms)
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

.sized{
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
  padding: .25rem 1rem;

  h3 {
    margin: 0;
  }

  h4 {
    margin: .25rem .5rem;
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

.email_text_container{
  display: flex;
  div {
    margin: .5rem .5rem .5rem 0;
  }
}
.removed_email {
  text-decoration: line-through;
  color: $very-light-gray;
}
</style>