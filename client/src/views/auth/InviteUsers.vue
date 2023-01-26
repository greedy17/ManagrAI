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
      <form v-if="true /*hasSlack*/" class="invite-form modal-form confirm-form form-margin-small">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Are you sure?</h3>
          </div>
          <div class="flex-row">
            <h4 class="invite-form__subtitle">
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
      <form v-if="true /*hasSlack*/" class="invite-form modal-form confirm-form form-margin-small">
        <div class="modal-header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Change Admin</h3>
          </div>
          <div class="flex-row">
            <img
              @click="handleCancel"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="filter: invert(30%); cursor: pointer"
            />
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
                  :options="team.list /* do not show the current admin */"
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
                style="width: 5rem; margin-right: 5%; height: 2rem"
              >
                Save
              </div>
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
      <form v-if="true /*hasSlack*/" class="invite-form modal-form" style="margin-top: 7.5rem">
        <div class="modal-header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Create a Team</h3>
          </div>
          <div class="flex-row">
            <img
              @click="handleCancel"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="filter: invert(30%); cursor: pointer"
            />
          </div>
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
                    isAdmin ? team.list.filter((user) => user.id !== getUser.id) : team.list
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
      <form v-if="true /*hasSlack*/" class="invite-form modal-form">
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
                  style="width: 33vw"
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
                  style="width: 33vw"
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

    <section class="header">
      <div class="profile-info">
        <div class="profile-info__img">
          <img src="@/assets/images/profile.svg" style="filter: invert(80%)" height="40px" alt="" />
        </div>
        <div class="profile-info__body">
          <div class="row__">
            <h2 @click="test">{{ getUser.fullName }}</h2>
            <!-- <span @click="selectingOption = !selectingOption" class="img-border">
              <img
                src="@/assets/images/more_horizontal.svg"
                style="margin-left: 8px"
                height="18px"
                alt=""
              />
            </span> -->

            <div class="img-border" @click="viewAdminPage" v-if="getUser.isStaff">
              <img
                style="filter: invert(40%); margin-left: 8px"
                src="@/assets/images/adminPanel.svg"
                class="nav-img"
                height="18px"
                alt=""
              />
            </div>
          </div>
          <h3 style="color: #41b883; background-color: #dcf8e9; padding: 4px; border-radius: 6px">
            {{ $store.state.user.organizationRef.name }}
          </h3>
          <small>{{ getUser.timezone }}</small>
          <div class="options__section">
            <button v-if="isAdmin" class="invite_button" type="submit" @click="showChangeAdmin">
              Change Admin
            </button>
            <button v-if="isAdmin" class="invite_button" type="submit" @click="handleNewTeam">
              Create New Team
            </button>

            <div class="tooltip">
              <button
                :disabled="team.list.length >= numberOfAllowedUsers"
                class="invite_button"
                type="submit"
                @click="handleInvite"
              >
                Invite Member

                <div v-if="team.list.length >= numberOfAllowedUsers">
                  <img
                    v-if="hasSlack"
                    style="height: 0.8rem; margin-left: 0.25rem"
                    src="@/assets/images/lock.svg"
                    alt=""
                  />
                </div>

                <div v-else>
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
                </div>
              </button>
              <small v-if="team.list.length >= numberOfAllowedUsers" class="tooltiptext"
                >User limit exceeded: {{ numberOfAllowedUsers }}</small
              >
            </div>
          </div>

          <!-- <div v-show="selectingOption" class="options">
            <p v-if="!updateInfoSelected" @click="updateInfo">Edit Info</p>
            <p v-if="!manageTeamSelected" @click="manageTeam">Manage Team</p>
            <div class="options__section">
              <button v-if="isAdmin" class="invite_button" type="submit" @click="showChangeAdmin">
                Change Admin
              </button>
              <button v-if="isAdmin" class="invite_button" type="submit" @click="handleNewTeam">
                Create New Team
              </button>

              <div class="tooltip">
                <button
                  :disabled="team.list.length >= numberOfAllowedUsers"
                  class="invite_button"
                  type="submit"
                  @click="handleInvite"
                >
                  Invite Member

                  <div v-if="team.list.length >= numberOfAllowedUsers">
                    <img
                      v-if="hasSlack"
                      style="height: 0.8rem; margin-left: 0.25rem"
                      src="@/assets/images/lock.svg"
                      alt=""
                    />
                  </div>

                  <div v-else>
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
                  </div>
                </button>
                <small class="tooltiptext">User limit exceeded: {{ numberOfAllowedUsers }}</small>
              </div>
            </div>
          </div> -->
        </div>
      </div>
    </section>

    <div class="main-content">
      <section v-if="updateInfoSelected">
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
          >
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                {{ getUser.timezone }}
              </p>
            </template>
          </Multiselect>
          <button class="invite_button" type="submit" @click="handleUpdate">
            Update
            <img
              style="height: 0.8rem; margin-left: 0.25rem"
              src="@/assets/images/logo.png"
              alt=""
            />
          </button>
        </form>
      </section>

      <section v-if="manageTeamSelected">
        <Invite
          class="invite-users__inviter"
          :handleEdit="handleEdit"
          :inviteOpen="inviteOpen"
          @cancel="handleCancel"
          @handleRefresh="refresh"
        />
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
      selectingOption: false,
      noSelection: true,
      manageTeamSelected: true,
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
    viewAdminPage() {
      this.$router.push({ name: 'Staff' })
    },
    test() {
      console.log(this.getUser)
    },
    manageTeam() {
      this.manageTeamSelected = true
      this.updateInfoSelected = false
      this.createNoteSelected = false
      this.editNoteSelected = false
      this.selectedTemplate = false
      this.selectingOption = false
    },
    updateInfo() {
      this.manageTeamSelected = false
      this.updateInfoSelected = true
      this.createNoteSelected = false
      this.editNoteSelected = false
      this.selectedTemplate = false
      this.selectingOption = false
    },
    createNote() {
      this.manageTeamSelected = false
      this.updateInfoSelected = false
      this.createNoteSelected = true
      this.editNoteSelected = false
      this.selectedTemplate = false
      this.selectingOption = false
    },
    editNote() {
      this.getTemplates()
      this.manageTeamSelected = false
      this.updateInfoSelected = false
      this.createNoteSelected = false
      this.editNoteSelected = true
      this.selectedTemplate = false
      this.selectingOption = false
    },
    selectTemplate(template) {
      this.selectedTemplate = template
    },
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
        this.usersList = team
          ? filterUsers.filter((user) => user.team !== team.id && !user.isTeamLead)
          : []
      } else {
        // If they are not an admin, show users in their team or in original team, depending on which team is selected
        if (team.id === this.originalTeam.id) {
          this.usersList = filterUsers.filter(
            (filteredUser) => filteredUser.team === this.getUser.team && !filteredUser.isTeamLead,
          )
        } else {
          this.usersList = filterUsers.filter(
            (filteredUser) =>
              filteredUser.team === this.originalTeam.id && !filteredUser.isTeamLead,
          )
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
            organization: this.$store.state.user.organizationRef.id,
            team_lead: this.teamLead.id,
          }
          const teamRes = await Organization.api.createNewTeam(data)
          const addTeamData = {
            users: [this.teamLead.id],
            team_id: teamRes.id,
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
        } catch (e) {
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
    async refresh() {
      this.team.refresh()
      this.inviteOpen = false
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
      const currentTeam = res.results.length
        ? res.results.filter((team) => team.id === this.getUser.team)[0]
        : null
      this.selectedTeam = currentTeam
      this.updateAvailableUsers(currentTeam)
    },
    setTime() {
      this.profileForm.field.timezone.value = this.selectedTimezone.value
    },
    showChangeAdmin() {
      this.changeAdminModal = !this.changeAdminModal
      this.selectingOption = false
    },
    handleInvite() {
      this.inviteOpen = !this.inviteOpen
      this.selectingOption = false
    },
    handleNewTeam() {
      this.newTeam = !this.newTeam
      this.selectingOption = false
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
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    numberOfAllowedUsers() {
      return this.$store.state.user.organizationRef.numberOfAllowedUsers
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
.header {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  height: 13vh;
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
.modal-header {
  width: 100%;
  margin-top: -1.5rem;
  display: flex;
  justify-content: space-between;
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
.profile-info {
  position: absolute;
  top: 6vh;
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
.main-content {
  margin-top: 15vh;
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid $soft-gray;
  border-radius: 100%;
  height: 26px;
  width: 26px;
  padding-right: 8px;
  cursor: pointer;
  background-color: white;
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
.update-container {
  background-color: $white;
  padding: 24px 16px;
  color: $base-gray;
  display: flex;
  align-items: flex-start;
  flex-direction: column;

  button {
    margin-left: -1px;
    margin-top: 16px;
  }

  // ::v-deep div {
  //   display: none !important;
  // }
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
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  text-align: center;
  margin-top: 8px;
  margin-left: 60px;
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

h2 {
  @include base-font-styles();
  font-weight: bold;
  text-align: center;
  font-size: 20px;
  margin-bottom: 2rem;
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
  color: white !important;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 13px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 160px;
  top: 60%;
  left: 38%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
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
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
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
  height: 40vh;
  // justify-content: space-evenly;
}
.modal-button {
  @include primary-button();
  box-shadow: none;
  margin-top: 1.5rem;
  height: 2.5rem;
  width: 19rem;
  font-size: 14px;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  // width: 90%;
  margin: 0 5%;
  letter-spacing: 1px;
  h4 {
    // font-size: 20px;
  }
}
.logo {
  height: 24px;
  margin-left: 0.25rem;
  margin-right: 0.5rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.confirm-form {
  width: 37vw;
  height: 33vh;
}
.form-margin-small {
  margin-top: 10rem;
}
</style>