<template>
  <div class="notes">
    <!-- <div class="alerts-header">
      <p v-if="!creating && !editing">
        Templates: <span class="gray-blue">{{ noteTemplates ? noteTemplates.length : 0 }}</span>
      </p>
      <p class="center" @click="cancel" v-else>
        <img src="@/assets/images/left.svg" height="14px" alt="" />
        Back
      </p>
      <button disabled class="green_button right-margin center-row side-wrapper" v-if="!isPaid && !editing">
        Create Template
        <label class="side-icon side-workflow">
          <span class="side-tooltip-single" style="top: -5px; right: 135px; width: 200px;">Upgrade your plan</span>
          <img
            class="shimmer"
            style="filter: invert(40%); margin-left: 6px;"
            src="@/assets/images/lock.svg"
            height="14px"
            alt=""
          />
        </label>
      </button>

      <button v-else-if="!creating && !editing && isPaid" @click="createNote" class="green_button">
        Create Template
      </button>

      <div v-else-if="creating">
        <button
          :disabled="!noteSubject || !noteBody"
          class="green_button"
          type="submit"
          @click="createTemplate"
          v-if="!savingTemplate"
        >
          Create
        </button>

        <div v-else>
          <PipelineLoader />
        </div>
      </div>

      <div v-else>
        <button @click="removeTemplate" class="delete">Delete</button>
        <button class="green_button" type="submit" @click="updateTemplate">Update</button>
      </div>
    </div> -->
    <Modal
      v-if="confirmDeleteModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), closeModals()
        }
      "
    >
    <!-- modal-form confirm-form -->
      <form v-if="true /*hasSlack*/" class="invite-form crm-form form-margin-small" style="height: 25vh;">
        <div class="header-crm">
          <div class="flex-row-wrapper inner-crm">
            <div class="flex-row-modal" style="margin: 0;">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title">Are you sure?</h3>
            </div>
            <div class="flex-row-modal" style="margin: 0;">
              <img
                @click="closeModals"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  margin-right: 5px;
                "
              />
            </div>
          </div>
        </div>
        <div class="flex-row-modal inner-crm" style="margin: 0; justify-content: flex-start; width: 90%;">
          <h4 class="card-text" style="margin-left: 0; margin-top: 0; margin-bottom: 0.75rem;">
            By clicking Delete, you will be removing 
            {{ this.deleteNote ? `${this.deleteNote.subject}` : 'this note' }}.
          </h4>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="confirm-cancel-container" style="width: 90%; margin-bottom: 0.6rem;">
            <div class="img-border-modal cancel-button" @click="closeModals" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem;">
              Cancel
            </div>
            <div class="img-border-modal red-button" @click="removeTemplate(deleteNote.id)" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem; margin-right: 5%;">
              Delete
            </div>
          </div>
          <!-- <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="onRevoke(removeApp)"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div> -->
        </div>
      </form>
    </Modal>

    <Modal
      v-if="createEditModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), closeModals()
        }
      "
    >
    <!-- modal-form confirm-form -->
      <form class="invite-form crm-form form-margin-small" style="height: 60vh;">
        <div class="header-crm">
          <div class="flex-row-wrapper inner-crm">
            <div class="flex-row-modal" style="margin: 0;">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title">{{createEditType === 'create' ? 'Create' : 'Edit'}} Template</h3>
            </div>
            <div class="flex-row-modal" style="margin: 0;">
              <img
                @click="closeModals"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  margin-right: 5px;
                "
              />
            </div>
          </div>
        </div>
        <div class="flex-row-modal inner-crm" style="margin: 0; justify-content: flex-start; width: 90%; padding-bottom: 0;">
          <!-- <h4 @click="test(deleteNote)" class="card-text" style="margin-left: 0; margin-top: 0; margin-bottom: 0.75rem;">
            By clicking Delete, you will be removing 
            {{ this.deleteNote ? `${this.deleteNote.subject}` : 'this note' }}.
          </h4> -->
          <div class="update-container">
            <input
              v-model="editSubject"
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
                  toolbar: null,
                },
                theme: 'snow',
                placeholder: 'your template...',
              }"
              v-model="editBody"
              class="message__box"
            />

            <div class="tooltip" style="display: flex; align-items: center">
              <input type="checkbox" id="shared" v-model="editShared" />
              <label class="small" for="shared">Share Template</label>
              <!-- <span class="tooltiptext">Share template with your team</span> -->
            </div>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="confirm-cancel-container" style="width: 90%; margin-bottom: 0.6rem; padding-top: 1rem;">
            <div class="img-border-modal cancel-button" @click="closeModals" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem;">
              Cancel
            </div>
            <div class="img-border-modal green_button" @click="saveNoteModal" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem; margin-right: 5%;">
              Save
            </div>
          </div>
          <!-- <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="onRevoke(removeApp)"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div> -->
        </div>
      </form>
    </Modal>
    
    <div class="integrations__cards">
      <div :key="i" v-for="(note, i) in noteTemplates">
        <div class="card">
          <div class="card__header" style="">
            <img style="height: 30px" src="@/assets/images/note.svg" />
          </div>
          <div class="card__body">
            <div style="display: flex">
              <h3 class="card__title">
                <!-- <img v-if="hasSlackIntegration" src="@/assets/images/dot.svg" class="green-filter" /> -->
                {{ note.subject }}
              </h3>
            </div>
            <p class="card-text" style="margin-bottom: 0;">
              Created by:
                <span class="gray-blue">{{
                  allUsers ? allUsers.filter((user) => user.id == note.user)[0].full_name : '---'
                }}</span>
            </p>
            <p class="card-text" style="margin-top: 0;">
              Shared: <span class="gray-blue">{{ note.is_shared ? 'Yes' : 'No' }}</span>
            </p>
            <div class="sep-button-container">
              <div class="separator"></div>
              <div style="display: flex; margin-top: 0.5rem;">
                <button @click="selectTemplate(note)" class="img-border" style="margin-right: 0.5rem;">
                  <img src="@/assets/images/pencil.svg" style="height: 13px" alt="" />
                </button>
                <button @click="confirmRemoveTemplate(note)" class="img-border">
                  <img src="@/assets/images/chat-trash.svg" class="filtered-red" style="height: 14px" alt="" />
                </button>
              </div>
              <!-- <button class="long-button" style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem;" @click="connectApp('SLACK')">
                Connect 
                <img 
                  src="@/assets/images/angle-small-right.svg" 
                  class="green-filter"
                  style="margin-top: 1px; margin-left: 0.5rem; height: 16px; font-weight: bold;"
                />
              </button> -->
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="card">
          <div class="card__header" style="">
            <img style="height: 30px" src="@/assets/images/note.svg" />
          </div>
          <div class="card__body">
            <div style="display: flex">
              <h3 class="card__title">
                <!-- <img v-if="hasSlackIntegration" src="@/assets/images/dot.svg" class="green-filter" /> -->
                {{ 'Create Template' }}
              </h3>
            </div>
            <p class="card-text" style="margin: 1.25rem 0;">
              Create your own note template
            </p>
            <div class="sep-button-container">
              <div class="separator"></div>
              <button @click="createNote" class="long-button">
                <!-- <img src="@/assets/images/pencil.svg" height="14px" alt="" /> -->
                Create Template
              </button>
              <!-- <button class="long-button" style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem;" @click="connectApp('SLACK')">
                Connect 
                <img 
                  src="@/assets/images/angle-small-right.svg" 
                  class="green-filter"
                  style="margin-top: 1px; margin-left: 0.5rem; height: 16px; font-weight: bold;"
                />
              </button> -->
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- <section v-if="!creating">
      <div v-if="noteTemplates.length" :class="editing ? 'update-container' : 'container-notes'">
        <section v-if="!editing">
          <div class="template" :key="i" v-for="(note, i) in noteTemplates">
            <div class="gray">
              {{ note.subject }}
              <button @click="selectTemplate(note)" class="img-border">
                <img src="@/assets/images/pencil.svg" height="14px" alt="" />
              </button>
            </div>
            <p>
              Created by:
              <span class="gray-blue">{{
                allUsers ? allUsers.filter((user) => user.id == note.user)[0].full_name : '---'
              }}</span>
            </p>
            <p>
              Shared: <span class="gray-blue">{{ note.is_shared ? 'Yes' : 'No' }}</span>
            </p>
          </div>
        </section>

        <section v-else>
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
                toolbar: null,
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
        </section>
      </div>

      <div v-else class="container-notes">
        <div class="empty-list">
          <section class="bg-img"></section>
          <h3>No templates found</h3>
          <p>Supercharge your note taking</p>
          <button @click="createNote" class="white_button">Create template</button>
        </div>
      </div>
    </section> -->

    <!-- <section v-else>
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
              toolbar: null,
            },
            theme: 'snow',
            placeholder: 'your template...',
          }"
          v-model="noteBody"
          class="message__box"
        />

        <div class="tooltip" style="display: flex; align-items: center">
          <input type="checkbox" id="shared" v-model="isShared" />
          <label class="small" for="shared">Share Template</label>
          <span class="tooltiptext">Share template with your team</span>
        </div>
      </div>
    </section> -->
  </div>
</template>
<script>
import User from '@/services/users'
import PipelineLoader from '@/components/PipelineLoader'
import { SObjects } from '@/services/salesforce'
import { quillEditor } from 'vue-quill-editor'
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

export default {
  name: 'ConfigureNotes',
  components: {
    quillEditor,
    PipelineLoader,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      allUsers: null,
      creating: false,
      editing: false,
      noteSubject: null,
      editSubject: null,
      noteBody: null,
      editBody: null,
      isShared: false,
      editShared: false,
      savingTemplate: false,
      selectedTemplate: null,
      deleteNote: null,
      createEditType: '',
      confirmDeleteModal: false,
      createEditModal: false,
    }
  },

  computed: {
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    noteTemplates() {
      return this.$store.state.templates
    },
    user() {
      return this.$store.state.user
    },
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    confirmRemoveTemplate(note) {
      this.deleteNote = note
      this.confirmDeleteModal = true
    },
    closeModals() {
      this.confirmDeleteModal = false
      this.createEditModal = false
      this.createEditType = ''
    },
    async getUsers() {
      try {
        const res = await SObjects.api.getObjectsForWorkflows('User')
        this.allUsers = res.results
      } catch (e) {
        console.log(e)
      }
    },
    createNote() {
      // this.creating = true
      this.createEditType = 'create'
      this.editSubject = this.noteSubject
      this.editBody = this.noteBody
      this.editShared = this.isShared
      this.createEditModal = true
    },
    // async createDefaultTemplate() {
    //   this.savingTemplate = true
    //   try {
    //     const res = await User.api.createTemplate({
    //       subject: 'Default Template',
    //       body: this.noteBody,
    //       is_shared: this.isShared,
    //       user: this.user.id,
    //     })
    //     this.$toast('Note template created successfully', {
    //       timeout: 2000,
    //       position: 'top-left',
    //       type: 'success',
    //       toastClassName: 'custom',
    //       bodyClassName: ['custom'],
    //     })
    //     this.$router.go()
    //   } catch (e) {
    //     console.log(e)
    //     this.$toast('Error creating template', {
    //       timeout: 2000,
    //       position: 'top-left',
    //       type: 'error',
    //       toastClassName: 'custom',
    //       bodyClassName: ['custom'],
    //     })
    //   }
    // },
    saveNoteModal() {
      console.log('this.createEditType', this.createEditType)
      if (!this.editSubject || !this.editBody) {
        this.$toast('Please fill out title and body', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      if (this.createEditType === 'create') {
        console.log('hit here')
        this.createTemplate()
      } else {
        this.selectedTemplate.subject = this.editSubject
        this.selectedTemplate.body = this.editBody
        this.selectedTemplate.is_shared = this.editShared
        this.updateTemplate()
      }
    },
    async createTemplate() {
      this.savingTemplate = true
      try {
        console.log('why do you refresh', {
          subject: this.editSubject,
          body: this.editBody,
          is_shared: this.editShared,
          user: this.user.id,
        })
        const res = await User.api.createTemplate({
          subject: this.editSubject,
          body: this.editBody,
          is_shared: this.editShared,
          user: this.user.id,
        })
        this.$store.dispatch('loadTemplates')
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
      }
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
        this.$store.dispatch('loadTemplates')
      } catch (e) {
        this.$toast('Error updating template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        // this.$router.go()
      }
    },
    selectTemplate(template) {
      this.selectedTemplate = template
      // this.editing = true
      this.createEditType = 'edit'
      this.editSubject = this.selectedTemplate.subject
      this.editBody = this.selectedTemplate.body
      this.editShared = this.selectedTemplate.is_shared
      this.createEditModal = true
    },
    async removeTemplate() {
      try {
        const res = await User.api.removeTemplate(this.deleteNote.id)
        this.$toast('Template removal successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        // this.$router.go()
        this.$store.dispatch('loadTemplates')
        this.closeModals()
      } catch (e) {
        this.$toast('Error removing template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    cancel() {
      this.editing = false
      this.creating = false
    },
  },
  created() {
    this.getUsers()
    this.$store.dispatch('loadTemplates')
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/modals';
.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

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

.notes {
  letter-spacing: 0.75px;
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  // margin-left: 80px;
  margin-top: 9vh;
}

.container-notes {
  // height: 85vh;
  overflow-y: scroll;
  padding: 16px;
  width: 40vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
}
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 60px;
  background-color: white;
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
.green_button {
  @include primary-button();
  max-height: 2rem;
  padding: 0.5rem 1.25rem;
  font-size: 12px;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.gray-blue {
  color: $light-gray-blue;
}
.template {
  border-bottom: 1px solid $soft-gray;
  padding-bottom: 16px;
  p {
    font-size: 13px;
  }

  div {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
.white_button {
  color: $dark-green;
  background-color: $white;
  border: 1px solid $dark-green;
  letter-spacing: 0.75px;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
  text-align: center;
}
.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $light-gray-blue;
  letter-spacing: 0.76px !important;

  .bg-img {
    background-image: url(../../../assets/images/logo.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 72px;
    width: 120px;
    opacity: 0.5;
  }
  h3 {
    color: $base-gray;
    margin-bottom: 0;
    margin-top: 12px;
  }
  p {
    font-size: 13px;
  }
}
.gray {
  font-weight: 400;
  color: $base-gray;
  background-color: $off-white;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 14px;
  letter-spacing: 1px;
  margin-left: -4px;
  margin-top: 4px;
}
.message__box {
  margin-top: -16px;
  margin-bottom: 8px;
  height: 30vh;
  width: 40vw;
  border-radius: 0.25rem;
  background-color: transparent;
}
.update-container {
  background-color: $white;
  // outline: 1px solid $soft-gray;
  padding: 30px;
  border-radius: 6px;
  // height: 85vh;
  color: $base-gray;
  display: flex;
  align-items: flex-start;
  flex-direction: column;

  button {
    margin-left: -1px;
    margin-top: 16px;
  }
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
.tooltip {
  position: relative;
  display: inline-block;
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 160px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  opacity: 0.7;

  /* Position the tooltip text - */
  position: absolute;
  z-index: 1;
  top: 2px;
  right: 105%;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}

input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 1.05ex;
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
  vertical-align: -8%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
.center {
  display: flex;
  align-items: center;
  cursor: pointer;

  img {
    filter: invert(40%);
    margin-right: 6px;
  }
}
.delete {
  background-color: $coral;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 8px 16px;
  margin-right: 8px;
}
.img-border {
  @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  img {
    filter: invert(40%);
  }
}
// Tooltip
.side-wrapper {
  display: flex;
  flex-direction: row;
}
.side-wrapper .side-icon {
  position: relative;
  // background: #FFFFFF;
  border-radius: 50%;
  padding: 12px;
  // margin: 20px 12px 0px 10px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  // outline: 1px solid $mid-gray;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip,
.side-wrapper .side-tooltip-single {
  display: block;
  width: 250px;
  height: auto;
  position: absolute;
  top: -10px; // for double line
  // top: 0; // for single line
  right: 30px;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip-single {
  width: 100px;
}
.side-wrapper .side-tooltip::before,
.side-wrapper .side-tooltip-single::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: 50%;
  right: -4%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip-single::before {
  bottom: 40%;
}
.side-wrapper:hover .side-icon .side-tooltip,
.side-wrapper:hover .side-icon .side-tooltip-single {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.side-wrapper:hover .side-icon span,
.side-wrapper:hover .side-icon .side-tooltip,
.side-wrapper:hover .side-icon .side-tooltip-single {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
// .side-wrapper .side-workflow:hover,
.side-wrapper:hover .side-workflow .side-tooltip,
.side-wrapper:hover .side-workflow .side-tooltip::before,
.side-wrapper:hover .side-workflow .side-tooltip-single,
.side-wrapper:hover .side-workflow .side-tooltip-single::before {
  // margin-top: 1rem;
  background: $grape;
  color: #ffffff;
}
.side-icon:hover {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  img {
    filter: invert(90%);
  }
}
.center-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.card {
  background-color: $white;
  // padding: 16px 24px;
  padding: 0.5rem 0.75rem;
  border: 1px solid $soft-gray;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  margin-right: 1rem;
  margin-bottom: 1rem;
  // width: 420px;
  // width: 320px;
  width: 18.5vw;
  min-height: 144px;
  transition: all 0.25s;

  &__header {
    display: flex;
    align-items: center;
    // justify-content: center;
    padding: 4px 0px;
    border-radius: 6px;
    margin-left: 12px;

    img {
      margin: 0;
      height: 25px;
    }
  }

  &__body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 12px;
    h3 {
      margin-top: 0.2rem;
      margin-bottom: 0;
      // margin: 0;
      padding: 0;
      font-size: 16px;
    }
    p {
      font-size: 12px;
    }
  }
}
.card-img-border {
  // padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
  width: 40px;
  // border: 1px solid $soft-gray;
  border-radius: 4px;
  margin-right: 0.15rem;
}
.integrations {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  // padding: 0px 0px 0px 96px;
  margin-top: 4rem;
  &__cards {
    display: flex;
    flex-direction: row;
    padding: 0.5rem 1.5rem;
    flex-wrap: wrap;
    justify-content: flex-start;
    // width: 96vw;
    margin-top: 4px;
  }
}
.invite-form {
  @include small-modal();
  min-width: 37vw;
  // min-height: 64vh;
  align-items: center;
  justify-content: space-between;
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
    // margin-top: -4rem;
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
.crm-form {
  height: 60vh;
  width: 50vw;
}
.form-margin-small {
  margin-top: 5rem;
}
.header-crm {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  display: flex;
  justify-content: center;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
}
.flex-row-wrapper {
  display: flex;
  justify-content: space-between;
}
.inner-crm {
  border-bottom: 1px solid $soft-gray;
  width: 90%;
  padding-bottom: 0.4rem;
  overflow-y: auto;
}
.flex-row-modal {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  margin: 0 5%;
  letter-spacing: 1px;
}
.confirm-cancel-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 94%
}
.img-border-modal {
  // @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  // padding: 4px 6px;
  margin-right: 8px;
  margin-top: 0.5rem;
}
.cancel-button {
  @include gray-button();
}
.red-button {
  @include button-danger();
}
.long-button {
  @include white-button();
  // color: $black;
  // color: $dark-green;
  border: 1px solid $soft-gray;
  cursor: pointer;
  width: 15vw;
  // border-radius: 0.75rem;
  display: flex;
  align-items: center;
  padding: 0.5rem;
  margin-top: 0.7rem;
  // margin-bottom: 0.25rem;
}
.filtered-red {
  filter: invert(43%) sepia(45%) saturate(682%) hue-rotate(308deg) brightness(109%) contrast(106%) !important;
}
.separator {
  border-top: 1px solid $soft-gray;
  width: 15vw;
  // margin: 0rem 0 0.1rem 0;
}
</style>