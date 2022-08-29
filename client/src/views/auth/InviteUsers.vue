<template>
  <div class="invite-users">
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
      <form v-if="true/*hasSlack*/" class="invite-form modal-form confirm-form">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Are you sure?</h3>
          </div>
          <div class="flex-row">
            <h4 class="invite-form__subtitle">Once you choose this person, you will lose all admin privileges, and the user you selected will gain admin priviledges.</h4>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="changeAdminSubmit"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 1rem; height: 2rem;"
                text="Save"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
              <div class="cancel-button" @click="handleConfirmCancel" style="margin-right: 2.5rem;">Cancel</div>
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <!-- Change Admin -->
    <Modal
      v-if="changeAdminModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleCancel()
        }
      "
    >
      <form v-if="true/*hasSlack*/" class="invite-form modal-form confirm-form">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Change Organization's Admin</h3>
          </div>
        </div>

        <div
          style="display: flex; justify-content: center; flex-direction: column; margin-top: -3rem"
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select New Admin"
                  v-model="newAdmin"
                  :options="team.list/* do not show the current admin */"
                  openDirection="below"
                  style="width: 26vw"
                  selectLabel="Enter"
                  label="email"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select New Admin
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
              <div
                @click="handleConfirm"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 1rem; height: 2rem;"
                >Save</div
              >
              <div class="cancel-button" @click="handleCancel" style="margin-right: 2.5rem;">Cancel</div>
            </template>
          </div>
        </div>
      </form>
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
      <form v-if="true/*hasSlack*/" class="invite-form modal-form">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Create a Team</h3>
          </div>
        </div>

        <div
          style="display: flex; justify-content: center; flex-direction: column; margin-top: -3rem"
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <input
                  placeholder="Team Name"
                  v-model="teamName"
                  style="width: 26vw"
                  class="template-input modal-input"
                  type="text"
                  name=""
                  id=""
                  :disabled="false/*savingTemplate*/"
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
                  :options="team.list"
                  openDirection="below"
                  style="width: 26vw"
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
                style="width: 5rem; margin-right: 1rem; height: 2rem;"
                text="Save"
                :loading="pulseLoading"
                >Save</PulseLoadingSpinnerButton
              >
              <div class="cancel-button" @click="handleCancel" style="margin-right: 2.5rem;">Cancel</div>
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
      <form v-if="true/*hasSlack*/" class="invite-form modal-form">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Add Members to Team</h3>
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
                  @select="updateAvailableUsers($event)"
                  :options="teamsList"
                  openDirection="below"
                  style="width: 26vw"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template slot="afterList">
                    <p class="multi-slot__more" @click="listUsers(slackMembers.nextCursor)">
                      Load More
                      <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                    </p>
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
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <!-- Make this users to add to team -->
                <Multiselect
                  placeholder="Select Users"
                  v-model="selectedUsers"
                  :options="usersList"
                  openDirection="below"
                  style="width: 26vw"
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
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="editTeamSubmit"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 1rem; height: 2rem;"
                text="Save"
                :loading="pulseLoading"
                >Save</PulseLoadingSpinnerButton
              >
              <div class="cancel-button" @click="handleCancel" style="margin-right: 2.5rem;">Cancel</div>
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <div v-if="noSelection">
      <figure
        @click="
          manageTeamSelected = true
          noSelection = false
          getTeams()
        "
        class="hover-img"
      >
        <img src="@/assets/images/managrTeam.png" />
        <figcaption>
          <h5>Manage <br />Team</h5>
        </figcaption>

        <div class="figure-title">
          <p>Manage your team <img src="@/assets/images/team.svg" height="16px" alt="" /></p>
          <small>Invite others to join you on Managr</small>
        </div>
      </figure>

      <figure
        @click="
          updateInfoSelected = true
          noSelection = false
        "
        class="hover-img"
      >
        <img src="@/assets/images/updateInfo.png" />
        <figcaption>
          <h5>Update<br />Info</h5>
        </figcaption>
        <div style="margin-top: 12px" class="figure-title">
          <p>Update Info <img src="@/assets/images/profile.svg" height="16px" alt="" /></p>
          <small>Update your profile information</small>
        </div>
      </figure>
      <figure
        @click="
          createNoteSelected = true
          noSelection = false
        "
        class="hover-img"
      >
        <img src="@/assets/images/createTemplate.png" />
        <figcaption>
          <h5>Create<br />Template</h5>
        </figcaption>
        <div style="margin-top: 8px" class="figure-title">
          <p>Create Template <img src="@/assets/images/list.svg" height="18px" alt="" /></p>
          <small>Create a template for your notes</small>
        </div>
      </figure>
      <figure
        @click="
          editNoteSelected = true
          noSelection = false
          getTemplates()
        "
        class="hover-img"
      >
        <img src="@/assets/images/editTemplate.png" />
        <figcaption>
          <h5>Edit <br />Templates</h5>
        </figcaption>
        <div style="margin-top: 16px" class="figure-title">
          <p>Edit Templates <img src="@/assets/images/pencil.svg" height="12px" alt="" /></p>
          <small>Edit your note templates</small>
        </div>
      </figure>
    </div>

    <section v-if="manageTeamSelected">
      <div class="invite-users__header">
        <h3 style="color: #4d4e4c">Manage Your Team</h3>
        <div>
          <button v-if="isAdmin" class="invite_button" type="submit" @click="showChangeAdmin">
            Change Admin
          </button>
          <button v-if="isAdmin" class="invite_button" type="submit" @click="handleNewTeam">
            Create New Team
          </button>
          <button class="invite_button" type="submit" @click="handleInvite">
            Invite Member
            <img
              v-if="hasSlack"
              style="height: 0.8rem; margin-left: 0.25rem"
              src="@/assets/images/slackLogo.png"
              alt=""
            />
            <img
              v-else
              style="height: 0.8rem; margin-left: 0.25rem"
              src="@/assets/images/logo.png"
              alt=""
            />
          </button>
        </div>
      </div>

      <Invite class="invite-users__inviter" :handleEdit="handleEdit" :inviteOpen="inviteOpen" @cancel="handleCancel" />
      <div class="wide">
        <button @click="homeView" class="invite_button">
          <img src="@/assets/images/back.svg" height="12px" alt="" />
        </button>
      </div>
    </section>

    <div v-if="updateInfoSelected">
      <section>
        <header class="invite-users__header">
          <h3 style="color: #4d4e4c">Update your Info</h3>

          <button class="invite_button" type="submit" @click="handleUpdate">
            Update
            <img
              style="height: 0.8rem; margin-left: 0.25rem"
              src="@/assets/images/logo.png"
              alt=""
            />
          </button>
        </header>

        <form class="update-container">
          <input
            v-model="profileForm.field.firstName.value"
            placeholder="First Name"
            :errors="profileForm.field.firstName.errors"
            id="user-input"
          />
          <input
            v-model="profileForm.field.lastName.value"
            placeholder="Last Name"
            :errors="profileForm.field.lastName.errors"
            id="user-input"
          />

          <Multiselect
            placeholder="Select Timezone"
            style="width: 16rem"
            v-model="selectedTimezone"
            @input="setTime"
            :options="timezones"
            openDirection="below"
            selectLabel="Enter"
            label="key"
            track-by="value"
          />
        </form>
        <div class="wide">
          <button @click="homeView" class="invite_button">
            <img src="@/assets/images/back.svg" height="12px" alt="" />
          </button>
        </div>
      </section>
    </div>

    <div v-if="createNoteSelected">
      <section>
        <header class="invite-users__header">
          <h3 style="color: #4d4e4c">Create Template</h3>

          <button
            :disabled="!noteSubject || !noteBody"
            class="invite_button"
            type="submit"
            @click="createTemplate"
            v-if="!savingTemplate"
          >
            Save Template
            <!-- <img style="height: 0.8rem; margin-left: 0.25rem" src="@/assets/images/logo.png" alt="" /> -->
          </button>

          <div v-else>
            <PipelineLoader />
          </div>
        </header>

        <div class="update-container">
          <input
            v-model="noteSubject"
            class="template-input"
            type="text"
            name=""
            id=""
            :disabled="savingTemplate"
            placeholder="Template Title"
          />

          <quill-editor
            :disabled="savingTemplate"
            ref="message-body"
            :options="{
              modules: {
                toolbar: [
                  [{ header: 1 }, { header: 2 }],
                  ['bold', 'italic', 'underline'],
                  [{ list: 'ordered' }, { list: 'bullet' }],
                ],
              },
              theme: 'snow',
              placeholder: 'Type out your template here.',
            }"
            v-model="noteBody"
            class="message__box"
          />

          <div class="tooltip" style="margin-top: 1rem; display: flex; align-items: center">
            <input type="checkbox" id="shared" v-model="isShared" />
            <label class="small" for="shared">Share Template</label>
            <span class="tooltiptext">Share template with your team</span>
          </div>
        </div>
        <div class="wide">
          <button @click="homeView" class="invite_button">
            <img src="@/assets/images/back.svg" height="12px" alt="" />
          </button>
        </div>
      </section>
    </div>

    <div v-if="editNoteSelected">
      <section>
        <header class="invite-users__header">
          <h3 style="color: #4d4e4c">Edit Templates</h3>

          <div v-if="selectedTemplate" class="row">
            <button class="invite_button" type="submit" @click="updateTemplate">
              Update Template
            </button>

            <button @click="removeTemplate" class="invite_button2">
              <img src="@/assets/images/trash.svg" height="18px" alt="" />
            </button>
          </div>
        </header>

        <div v-if="noteTemplates" class="update-container">
          <div class="centered" v-if="!noteTemplates.length">
            <p>Nothing here yet... \_("/)_/</p>
          </div>

          <div class="row" v-else>
            <template v-if="!selectedTemplate">
              <div
                @click="selectTemplate(template)"
                class="small-container"
                v-for="(template, i) in noteTemplates"
                :key="i"
              >
                <div class="small-container__head">
                  <p>{{ template.subject }}</p>
                </div>
                <div class="small-container__body">
                  <p v-html="template.body"></p>
                </div>
              </div>
            </template>

            <div v-else>
              <input
                v-model="selectedTemplate.subject"
                class="template-input"
                type="text"
                name=""
                id=""
                :disabled="savingTemplate"
                placeholder="Template Title"
              />
              <quill-editor
                :disabled="savingTemplate"
                ref="message-body"
                :options="{
                  modules: {
                    toolbar: [
                      [{ header: 1 }, { header: 2 }],
                      ['bold', 'italic', 'underline'],
                      [{ list: 'ordered' }, { list: 'bullet' }],
                    ],
                  },
                  theme: 'snow',
                  placeholder: 'Type out your template here.',
                }"
                v-model="selectedTemplate.body"
                class="message__box"
              />
              <div class="align-start">
                <input type="checkbox" id="editShared" v-model="selectedTemplate.is_shared" />
                <label class="small" for="editShared">Share Template</label>
              </div>
            </div>
          </div>
        </div>
        <div class="wide">
          <button
            v-if="selectedTemplate"
            @click="selectedTemplate = !selectedTemplate"
            class="invite_button"
          >
            <img src="@/assets/images/back.svg" height="12px" alt="" />
          </button>
          <button v-else @click="homeView" class="invite_button">
            <img src="@/assets/images/back.svg" height="12px" alt="" />
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import CollectionManager from '@/services/collectionManager'
import Modal from '@/components/InviteModal'
import FormField from '@/components/forms/FormField'
import PipelineLoader from '@/components/PipelineLoader'
import Invite from '../settings/_pages/_Invite'
import User from '@/services/users'
import Organization from '@/services/organizations'
import { UserProfileForm } from '@/services/users/forms'
import { quillEditor } from 'vue-quill-editor'
import moment from 'moment-timezone'

export default {
  name: 'InviteUsers',
  components: {
    Invite,
    Modal,
    FormField,
    quillEditor,
    PulseLoadingSpinnerButton,
    PipelineLoader,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      noSelection: true,
      manageTeamSelected: false,
      updateInfoSelected: false,
      createNoteSelected: false,
      editNoteSelected: false,
      selectedTemplate: null,
      noteTemplates: null,
      isShared: false,
      savingTemplate: false,
      noteSubject: null,
      noteBody: null,
      inviteOpen: false,
      editTeam: false,
      newTeam: false,
      changeAdminModal: false,
      changeAdminConfirmModal: false,
      pulseLoading: false,
      newAdmin: null,
      teamName: '',
      teamLead: '',
      team: CollectionManager.create({ ModelClass: User }),
      teamsList: [],
      originalTeam: null,
      selectedTeam: null,
      selectedUsers: [],
      usersList: [],
      selectedTimezone: null,
      user: this.getUser,
      timezones: moment.tz.names(),
      profileForm: new UserProfileForm({}),
      loading: false,
    }
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    homeView() {
      this.noSelection = true
      this.manageTeamSelected = false
      this.updateInfoSelected = false
      this.createNoteSelected = false
      this.editNoteSelected = false
      this.selectedTemplate = false
    },
    selectTemplate(template) {
      this.selectedTemplate = template
    },
    // truncateText(text, length) {
    //   if (text.length <= length) {
    //     return text.replace(/(<([^>]+)>)/gi, '')
    //   }

    //   return text.replace(/(<([^>]+)>)/gi, '').substr(0, length) + '\u2026'
    // },
    async updateTemplate() {
      try {
        const res = await User.api.updateTemplate(this.selectedTemplate.id, this.selectedTemplate)
        this.$toast('Note template update successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error updating template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.homeView()
      }
    },
    updateAvailableUsers(team, users) {
      let filterUsers
      if (this.team.list.length) {
        filterUsers = this.team.list
      } else {
        filterUsers = users
      }
      if (this.isAdmin) {
        // If they are an admin, show all users except the ones in the selected team
        this.usersList = filterUsers.filter(user => user.team !== team.id && !user.isTeamLeader)
      } else {
        // If they are not an admin, show users in their team or in original team, depending on which team is selected
        if (team.id === this.originalTeam.id) {
          this.usersList = filterUsers.filter(filteredUser => filteredUser.team === this.getUser.team && !filteredUser.isTeamLeader)
        } else {
          this.usersList = filterUsers.filter(filteredUser => filteredUser.team === this.originalTeam.id && !filteredUser.isTeamLeader)
        }
      }
    },
    async removeTemplate() {
      try {
        const res = await User.api.removeTemplate(this.selectedTemplate.id)
        this.$toast('Template removal successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error removing template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.homeView()
      }
    },
    async getTemplates() {
      try {
        const res = await User.api.getTemplates()
        this.noteTemplates = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async createTemplate() {
      this.savingTemplate = true
      try {
        const res = await User.api.createTemplate({
          subject: this.noteSubject,
          body: this.noteBody,
          is_shared: this.isShared,
          user: this.getUser.id,
        })
        this.$toast('Note template created successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
        this.$toast('Error creating template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.savingTemplate = false
        this.noteSubject = null
        this.noteBody = null
        this.isShared = null
        this.homeView()
      }
    },
    async changeAdminSubmit() {
      this.pulseLoading = true
      if (!this.newAdmin || !this.newAdmin.id === this.getUser.id) {
        setTimeout(() => {
          console.log('Please choose a new admin')
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
            new_admin: this.newAdmin.id
          }
          const teamRes = await Organization.api.changeAdmin(data)
          this.refresh()
          setTimeout(() => {
            this.handleCancel()
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
        } catch(e) {
          console.log("Error: ", e)
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
    async createTeamSubmit() {
      this.pulseLoading = true
      if (!this.teamLead || !this.teamName) {
        setTimeout(() => {
          console.log('Please submit all info')
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
            organization: this.$store.state.user.organizationRef.id,
            team_lead: this.teamLead.id
          }
          const teamRes = await Organization.api.createNewTeam(data)
          const addTeamData = {
            users: [this.teamLead.id],
            team_id: teamRes.id
          }
          await Organization.api.addTeamMember(addTeamData)
          this.refresh()
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
        } catch(e) {
          console.log("Error: ", e)
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
          console.log('Please submit all info')
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
          const userIds = this.selectedUsers.map(user => user.id)
          const addTeamData = {
            users: userIds,
            team_id: this.selectedTeam.id
          }
          await Organization.api.addTeamMember(addTeamData)
          this.refresh()
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
        } catch(e) {
          console.log("Error: ", e)
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
    async refresh() {
      this.team.refresh()
    },
    async getTeams() {
      const res = await Organization.api.listTeams(this.getUser.id)
      const teamList = [res.results[0]]
      for (let i = 1; i < res.results.length; i++) {
        if (res.results[i].team_lead === this.getUser.id) {
          teamList.push(res.results[i])
        }
      }
      this.teamsList = teamList
      this.originalTeam = res.results[0]
      const currentTeam = res.results.filter(team => team.id === this.getUser.team)[0]
      this.selectedTeam = currentTeam
      this.updateAvailableUsers(currentTeam)
    },
    setTime() {
      this.profileForm.field.timezone.value = this.selectedTimezone.value
    },
    showChangeAdmin() {
      this.changeAdminModal = !this.changeAdminModal
    },
    handleInvite() {
      this.inviteOpen = !this.inviteOpen
    },
    handleNewTeam() {
      this.newTeam = !this.newTeam
    },
    handleEdit() {
      this.editTeam = !this.editTeam
    },
    handleConfirm() {
      this.changeAdminConfirmModal = !this.changeAdminConfirmModal
      this.changeAdminModal = !this.changeAdminModal
    },
    handleCancel() {
      this.inviteOpen = false
      this.editTeam = false
      this.newTeam = false
      this.changeAdminModal = false
    },
    handleConfirmCancel() {
      this.changeAdminConfirmModal = false
      this.changeAdminModal = !this.changeAdminModal
    },
    handleUpdate() {
      this.loading = true
      User.api
        .update(this.getUser.id, this.profileForm.value)
        .then((response) => {
          this.$toast('Sucessfully updated profile info', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.$store.dispatch('updateUser', User.fromAPI(response.data))

          this.resetProfileForm()
        })
        .catch((e) => {
          console.log(e)
          this.resetProfileForm()
        })
    },
    resetProfileForm() {
      this.profileForm.firstName = this.getUser.firstName
      this.profileForm.lastName = this.getUser.lastName
      this.profileForm.timezone = this.getUser.timezone
      this.loading = false
    },
  },
  async created() {
    this.getTemplates()
    this.profileForm = new UserProfileForm({
      firstName: this.getUser.firstName,
      lastName: this.getUser.lastName,
      timezone: this.getUser.timezone,
    })
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
    this.refresh()
  },
  mounted() {
    if (this.isAdmin) {
      this.newAdmin = this.getUser
    }
  },
  computed: {
    getUser() {
      return this.$store.state.user
    },
    isAdmin() {
      return this.$store.state.user.isAdmin
    },
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

::v-deep .ql-toolbar.ql-snow {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
::v-deep .ql-container.ql-snow {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

.message__box {
  margin-bottom: 2rem;
  height: 24vh;
  width: 36vw;
  border-radius: 0.25rem;
  background-color: transparent;
}
.template-input {
  border: 1px solid #ccc;
  border-radius: 0.3rem;
  padding-left: 1rem;
  height: 50px;
  width: 36vw;
  font-family: inherit;
  margin-bottom: 1rem;
}
.template-input:focus {
  outline: none;
}
.update-container {
  background-color: $white;
  border: 1px solid #e8e8e8;
  color: $base-gray;
  width: 60vw;
  min-height: 40vh;
  overflow: visible;
  padding: 1.5rem 0rem 1.5rem 1rem;
  border-radius: 5px;
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 16rem;
  margin-bottom: 1rem;
  font-family: $base-font-family;
}
#user-input:focus {
  outline: none;
}
.invite-users {
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-top: 4rem;
  padding-bottom: 1rem;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 60vw;
    padding: 0.25rem;
  }

  &__inviter {
    margin-top: 2rem;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  text-align: center;
  font-size: 20px;
  margin-bottom: 2rem;
}

.invite_button {
  color: $dark-green;
  background-color: white;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 8px 12px;
  margin-left: .5rem;
  font-size: 14px;
  border: 1px solid #e8e8e8;
}
.invite_button2 {
  background-color: white;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 6px 12px;
  border: 1px solid #e8e8e8;
}
.invite_button:disabled {
  color: $base-gray;
  background-color: $soft-gray;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 8px 12px;
  font-weight: 400px;
  font-size: 14px;
  border: 1px solid #e8e8e8;
}

.invite_button:hover,
.invite_button2:hover {
  cursor: pointer;
  transform: scale(1.025);
  box-shadow: 1px 2px 3px $mid-gray;
}
input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
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
input[type='checkbox'] {
  line-height: 2.1ex;
}
input[type='checkbox'] {
  position: absolute;
  left: -999em;
}
input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
input[type='checkbox'] + label::before {
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
.small {
  font-size: 12px;
}
@mixin epic-sides() {
  position: relative;
  z-index: 1;

  &:before {
    position: absolute;
    content: '';
    display: block;
    top: 0;
    left: -5000px;
    height: 100%;
    width: 15000px;
    z-index: -1;
    @content;
  }
}

@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}

.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 200px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 38vh;
}
.small-container {
  box-shadow: 1px 1px 2px 1px #ccc;
  border: 1px solid white;
  border-radius: 6px;
  width: 250px;
  height: 110px;
  overflow: hidden;
  cursor: pointer;
  &__head {
    border-bottom: 1px solid #ccc;
    padding: 1px 8px;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 0.5px;
    height: 40px;
    display: flex;
    justify-content: flex-start;
    background-color: $dark-green;
    color: white;
  }
  &__body {
    display: flex;
    justify-content: flex-start;
    padding: 4px;
    opacity: 0.8;
    font-size: 12px;
  }
}
.small-container:hover {
  opacity: 0.7;
}
.row {
  padding-left: 1.5rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.hover-img {
  background-color: white;
  border: 1px solid white;
  box-shadow: 1px 1px 2px 1px #ccc;
  color: #fff;
  display: inline-block;
  margin: 8px;
  max-width: 320px;
  min-width: 240px;
  height: 275px;
  overflow: hidden;
  position: relative;
  text-align: center;
  width: 100%;
  border-radius: 8px;
  cursor: pointer;
}

.hover-img * {
  box-sizing: border-box;
  transition: all 0.45s ease;
}

.hover-img:before,
.hover-img:after {
  background-color: rgba(0, 0, 0, 0.5);
  border-top: 2px solid rgba(0, 0, 0, 0.5);
  border-bottom: 2px solid rgba(0, 0, 0, 0.5);
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  content: '';
  transition: all 0.3s ease;
  z-index: 1;
  opacity: 0;
  transform: scaleY(2);
}

.hover-img img {
  vertical-align: top;
  max-width: 100%;
  backface-visibility: hidden;
}

.hover-img figcaption {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  align-items: center;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: 1.1em;
  opacity: 0;
  z-index: 2;
  transition-delay: 0.1s;
  font-size: 24px;
  font-family: sans-serif;
  font-weight: 400;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.hover-img:hover:before,
.hover-img:hover:after {
  transform: scale(1);
  opacity: 1;
}

.hover-img:hover > img {
  opacity: 0.7;
}

.hover-img:hover figcaption {
  opacity: 1;
}
.wide {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
.figure-title {
  img {
    margin-left: 6px;
    filter: invert(20%);
    visibility: hidden;
  }
  p {
    font-size: 18px;
    display: flex;
    align-items: center;
  }
  background-color: $dark-green;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  padding: 8px;
  font-weight: bold;
  border-radius: 2px;

  small {
    color: $base-gray;
    margin-top: -8px;
    letter-spacing: 0.5px;
  }
}
.align-start {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 3rem;
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
.invert {
  filter: invert(80%);
}
.header {
  width: 100%;
  margin-top: -1rem;
}
// form {
//   width: 100%;
//   background-color: $white;
//   height: 50vh;
//   justify-content: space-evenly;
// }
.invite-button {
  background-color: $dark-green;
  color: white;
  margin-top: 2.5rem;
  width: 15vw;
  font-size: 16px;
  box-shadow: none;
}
// button {
//   @include primary-button();
//   margin-top: 1.25rem;
//   height: 2.5rem;
//   width: 19rem;
//   font-size: 14px;
// }
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
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.cancel-button {
  margin-top: 1rem;
  position: relative;
  right: 1px;
  color: $gray;
  &:hover {
    cursor: pointer;
  }
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
.modal-form {
  width: 100%;
  background-color: $white;
  height: 50vh;
  // justify-content: space-evenly;
}
.modal-button {
  @include primary-button();
  box-shadow: none;
  margin-top: 1.25rem;
  height: 2.5rem;
  width: 19rem;
  font-size: 14px;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  width: 90%;
  margin: 0 auto;
  letter-spacing: 1px;
  h4 {
    // font-size: 20px;
  }
}
.logo {
  height: 24px;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.confirm-form {
  width: 37vw;
  height: 40vh;
}
</style>