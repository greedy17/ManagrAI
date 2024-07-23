<template>
  <div class="contacts fadein">
    <Modal v-if="googleModalOpen" class="bio-modal">
      <div class="bio-container">
        <header>
          <p style="font-size: 20px">
            {{
              currentContact.journalist_ref.first_name +
              ' ' +
              currentContact.journalist_ref.last_name
            }}
          </p>

          <!-- <div class="row">
            <button
              :disabled="bioLoading || loadingTags"
              @click="updateContact(currentContact.id)"
              class="no-borders"
            >
              <img
                style="filter: invert(40%)"
                src="@/assets/images/refresh-pr.svg"
                height="18px"
                alt=""
              />
            </button>
          </div> -->
        </header>

        <section v-if="!bioLoading">
          <div class="bio-body" v-html="currentContact.bio"></div>

          <aside>
            <img
              v-for="(url, i) in currentContact.images"
              :key="i"
              :src="`${url}`"
              height="24px"
              alt=""
            />
          </aside>
        </section>

        <section v-else>
          <div style="height: 180px" class="bio-body">
            <div class="loading-small">
              <p style="margin-right: 8px">Updating bio</p>
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>

          <aside></aside>
        </section>

        <footer>
          <div class="rows">
            <div v-for="(tag, i) in currentContact.tags" :key="i" class="user-tag">
              <img src="@/assets/images/tags.svg" height="12px" alt="" />
              {{ tag }}
              <div @click="modifyTags('remove', tag)" class="remove">
                <img src="@/assets/images/close.svg" height="14px" alt="" />
              </div>
            </div>
          </div>
          <div class="row">
            <button
              class="secondary-button"
              :disabled="bioLoading || loadingTags"
              @click="toggleGoogleModal"
            >
              Close
            </button>
            <button
              :disabled="bioLoading || loadingTags"
              class="primary-button"
              @click="openPitchModal()"
            >
              Pitch
            </button>
          </div>
        </footer>
      </div>
    </Modal>
    <Modal v-if="detailsModalOpen" class="delete-modal">
      <div style="height: 200px" class="delete-container">
        <header style="font-size: 20px"></header>
        <main style="height: 100px">
          <h2 style="margin-bottom: 16px">Updating Contact</h2>
          <div class="row">
            This will only take a moment
            <div style="margin-left: 12px" class="loading-small">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>

          <!-- <div style="margin-top: 20px" class="row">
            <button @click="closeDeleteModal" class="secondary-button">Cancel</button>
            <button @click="deleteContact(contactId)" class="red-button">Delete</button>
          </div> -->
        </main>
      </div>
    </Modal>

    <!-- <Modal class="bio-modal med-modal" >
      <div class="bio-container med-container">
        <header>
          <p>Updating Journalist bio</p>
        

        <div style="margin-top: 40px; margin-bottom: 48px; height: 100px; width: 100%">
          <div class="input-container-small">
            <textarea
              :disabled="loadingPitch"
              style="border: none; outline: none; padding: 16px 8px; width: 100%"
              class="area-input text-area-input"
              type="text"
              v-model="contactOrg"
              rows="5"
              v-autoresize
              placeholder="Provide company name and pitch details..."
            />
          </div>
          <div style="font-size: 14px; margin: 12px 0 0 4px" class="row">
            <img src="@/assets/images/profile.svg" height="12px" alt="" />
            <p style="margin: 0 0 0 4px">
              Managr will generate pitching tips based on this information
            </p>
          </div>
        </div>

        <footer>
          <div></div>
       
        </footer>
      </div>
    </Modal> -->
    <Modal v-if="pitchModalOpen" class="bio-modal med-modal">
      <div class="bio-container med-container">
        <header>
          <p style="font-size: 22px; margin: 8px 0">
            Pitch
            {{
              currentContact.journalist_ref.first_name +
              ' ' +
              currentContact.journalist_ref.last_name
            }}
          </p>

          <div @click="togglePitchModal">
            <img
              style="cursor: pointer"
              class="right-mar img-highlight"
              src="@/assets/images/close.svg"
              height="18px"
              alt=""
            />
          </div>
        </header>

        <div
          v-show="!showingEditor"
          style="
            margin-top: 40px;
            margin-bottom: 48px;
            min-height: 120px;
            width: 100%;
            height: fit-content;
          "
        >
          <div class="input-container-small">
            <textarea
              :disabled="loadingPitch"
              style="border: none; outline: none; padding: 16px 8px; width: 100%"
              class="area-input text-area-input"
              type="text"
              v-model="content"
              rows="5"
              v-autoresize
              placeholder="Paste your pitch here..."
            />
          </div>
          <div style="font-size: 14px; margin: 12px 0 0 4px" class="row">
            <img src="@/assets/images/profile.svg" height="12px" alt="" />
            <p style="margin: 0 0 0 4px">
              Managr will automatically personalize your pitch based on the Journalist's bio
            </p>
          </div>
        </div>

        <div
          v-show="showingEditor"
          style="
            position: relative;
            margin-top: 24px;
            margin-bottom: 64px;
            min-height: 120px;
            height: fit-content;
          "
        >
          <div class="row">
            <div
              class="row"
              style="
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.135);
                width: 100%;
              "
            >
              <p style="margin: 0; padding: 0; font-size: 18px; margin-right: 8px">From:</p>

              <p class="e-container" style="margin: 0">{{ user.email }}</p>
            </div>

            <!-- <div
              class="row"
              style="
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.135);
                width: 50%;
              "
            >
              <p style="margin: 0; padding: 0; font-size: 18px; margin-right: 8px">Bcc:</p>
              <p :title="bccEmail" class="b-container" style="margin: 0">{{ bccEmail }}</p>
            </div> -->
          </div>

          <div style="position: relative">
            <p
              style="margin: 0; padding: 0; font-size: 18px; position: absolute; left: 0; top: 20px"
            >
              To:
            </p>
            <input
              style="margin-bottom: 0; padding-left: 26px"
              class="primary-input-underline"
              v-model="currentContact.journalist_ref.email"
              :class="{
                coraltext: !currentContact.journalist_ref.verified,
                greenText: currentContact.journalist_ref.verified,
              }"
              type="email"
              :disabled="currentContact.journalist_ref.verified"
            />

            <div
              v-if="currentContact.journalist_ref.verified"
              class="row green-img abs-placed"
              style="top: 35%"
            >
              <img src="@/assets/images/shield-check.svg" height="18px" alt="" />
            </div>
            <div v-else class="abs-placed red-img" style="top: 35%">
              <img src="@/assets/images/shield-x.svg" height="14px" alt="" />
            </div>
          </div>

          <div style="position: relative; margin-bottom: 8px">
            <p
              style="margin: 0; padding: 0; font-size: 18px; position: absolute; left: 0; top: 20px"
            >
              Subject:
            </p>
            <input
              class="primary-input-underline"
              v-model="subject"
              type="text"
              placeholder=""
              style="padding-left: 64px"
              :disabled="loadingPitch || sendingEmail"
            />
          </div>

          <quill-editor
            :disabled="loadingPitch || sendingEmail"
            ref="quill"
            :options="{
              modules: {
                toolbar: toolbarOptions,
              },
              theme: 'snow',
              placeholder: '',
            }"
            v-model:content="revisedPitch"
            class="text-editor"
          />

          <div v-if="loadingPitch" style="margin-left: 12px" class="loading-small-absolute">
            <p>Updating content</p>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>

        <footer>
          <div></div>
          <div class="row">
            <button class="secondary-button" @click="togglePitchModal">Cancel</button>

            <button
              v-if="!showingEditor"
              :disabled="!content"
              class="primary-button"
              @click="rewritePitch"
            >
              Continue
            </button>

            <button
              v-else
              :disabled="loadingPitch || sendingEmail"
              class="primary-button"
              @click="sendEmail"
            >
              Send Email
              <div v-if="sendingEmail" style="margin-left: 12px" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </footer>
      </div>
    </Modal>
    <Modal v-if="deleteModalOpen" class="delete-modal">
      <div class="delete-container">
        <header style="font-size: 20px" @click="closeDeleteModal">
          <p>x</p>
        </header>
        <main>
          <h2>Delete Contact</h2>
          <p>Are you sure you want to delete this contact ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="closeDeleteModal" class="secondary-button">Cancel</button>
            <button @click="deleteContact(contactId)" class="red-button">Delete</button>
          </div>
        </main>
      </div>
    </Modal>

    <Modal class="bio-modal med-modal" v-if="contactsModalOpen">
      <div class="bio-container med-container">
        <header>
          <h2 style="margin: 12px 0">Add Contact</h2>
        </header>

        <div style="margin-top: 16px; margin-bottom: 24px; min-height: 120px; width: 100%">
          <label for="contact">Contact Name</label>
          <input
            :disabled="loadingContacts"
            class="primary-input"
            type="text"
            name="contact"
            v-model="contactName"
          />
          <label for="outlet">Outlet Name</label>
          <input
            :disabled="loadingContacts"
            class="primary-input"
            type="text"
            name="outlet"
            v-model="outletName"
          />
          <label for="details">Your company details</label>
          <div class="input-container-small">
            <textarea
              :disabled="loadingContacts"
              style="
                border: none;
                outline: none;
                padding: 16px 8px;
                width: 100%;
                max-height: 100px !important;
              "
              class="area-input text-area-input"
              type="text"
              v-model="orgInfo"
              rows="2"
              v-autoresize
              placeholder="Provide company name and pitch details..."
              name="details"
            />
          </div>
          <div style="font-size: 14px; margin: 12px 0 0 4px" class="row">
            <img src="@/assets/images/profile.svg" height="12px" alt="" />
            <p style="margin: 0 0 0 4px">
              Managr will generate pitching tips based on this information
            </p>
          </div>
        </div>

        <footer>
          <div></div>
          <div class="row">
            <button
              class="secondary-button"
              :disabled="loadingContacts"
              @click="toggleContactsModal"
            >
              Cancel
            </button>
            <button
              @click="getJournalistBio"
              :disabled="loadingContacts || !orgInfo || !outletName || !contactName"
              class="primary-button"
            >
              Continue
              <div v-if="loadingContacts" style="margin-left: 12px" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </footer>
      </div>
    </Modal>

    <Modal v-if="bioModalOpen" class="bio-modal">
      <div class="bio-container">
        <header>
          <p style="font-size: 20px">New Contact</p>
        </header>

        <section>
          <div class="bio-body" v-html="newContactBio"></div>

          <aside>
            <img
              v-for="(url, i) in newContactImages"
              :key="i"
              :src="`${url}`"
              height="24px"
              alt=""
            />
          </aside>
        </section>

        <footer>
          <div></div>
          <div class="row">
            <button class="secondary-button" :disabled="savingContact" @click="toggleBioModal">
              Cancel
            </button>
            <button :disabled="savingContact" class="primary-button" @click="saveContact">
              Save
              <div v-if="savingContact" style="margin-left: 12px" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </footer>
      </div>
    </Modal>

    <header></header>

    <div class="space-between">
      <div class="row">
        <div style="margin-right: 16px" class="relative">
          <p style="margin-top: -8px" class="not-mobile">Saved Contacts</p>
          <!-- <button
            style="padding-top: 11px; padding-bottom: 11px"
            @click="toggleUserDropdown"
            class="secondary-button"
          >
            <img style="margin-right: 8px" src="@/assets/images/profile.svg" height="12px" alt="" />
            {{
              !selectedUser
                ? 'All'
                : selectedUser.fullName
                ? selectedUser.fullName
                : selectedUser.full_name
            }}
            <img style="margin-left: 8px" src="@/assets/images/dropdown.svg" height="14px" alt="" />
          </button> -->

          <div style="left: 0" v-if="showUsers" class="dropdown">
            <div class="dropdown-header">
              <h3>Select User</h3>
              <img
                @click="toggleUserDropdown"
                src="@/assets/images/close.svg"
                class="pointer"
                height="18px"
                alt=""
              />
            </div>

            <div style="margin: 8px 0 16px 0; padding-right: 12px">
              <div style="width: 100%" class="input">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
                <input v-model="searchUsersText" class="search-input" :placeholder="`Search...`" />
                <img
                  v-if="searchUsersText"
                  @click="clearUsersText"
                  src="@/assets/images/close.svg"
                  class="pointer"
                  height="12px"
                  alt=""
                />
              </div>
            </div>

            <!-- <div class="dropdown-body">
              <div class="col">
                <div v-if="!searchUsersText" @click="selectAllUsers" class="dropdown-item">All</div>
                <div
                  @click="selectUser(user)"
                  class="dropdown-item"
                  v-for="(user, i) in allUsers"
                  :key="i"
                >
                  {{ user.full_name }}
                </div>
              </div>
            </div> -->

            <div class="dropdown-footer"></div>
          </div>
        </div>
      </div>

      <div class="search">
        <div class="input">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
              fill="currentColor"
            ></path>
          </svg>
          <input
            v-model="searchContactsText"
            class="search-input"
            :placeholder="`Search contacts...`"
          />
          <img
            v-if="searchContactsText"
            @click="clearSearchText"
            src="@/assets/images/close.svg"
            class="pointer"
            height="12px"
            alt=""
          />
        </div>
      </div>
    </div>

    <div class="top-row top-padding">
      <aside>
        <div style="margin-left: 2px" class="row">
          <img src="@/assets/images/tags.svg" height="14px" alt="" />
          <h3>Tags</h3>
        </div>

        <div class="checkbox-list">
          <ul v-if="tags.length">
            <li v-for="tag in tagCounts" :key="tag.name">
              <label class="custom-checkbox">
                <input type="checkbox" id="checkbox" :value="tag" v-model="selectedTags" />
                <span class="checkmark"></span>
                {{ tag.name }} <span>({{ tag.count }})</span>
              </label>
            </li>
          </ul>

          <small v-else> Apply tags to organize journalists into lists. </small>
        </div>
      </aside>

      <section>
        <div class="row" style="padding-bottom: 8px">
          <div style="font-size: 16px" v-if="loading" class="loading-small">
            <p style="margin: 0; margin-right: 8px">Gathering your contacts</p>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
          <h3 v-else style="font-size: 16px">Showing: {{ filteredContactList.length }} contacts</h3>
          <button
            @click="toggleContactsModal"
            v-if="!loading"
            class="secondary-button"
            style="margin-left: 12px"
          >
            <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Contact
          </button>
        </div>

        <div class="cards-container">
          <div v-for="(contact, i) in filteredContactList" :key="i" class="contact-card">
            <header style="position: relative">
              <div class="contact-header">
                <p class="base-font">
                  {{ contact.journalist_ref.first_name + ' ' + contact.journalist_ref.last_name }}
                </p>
                <p style="font-size: 14px">
                  <!-- <img src="@/assets/images/building.svg" height="13px" alt="" /> -->
                  {{ contact.journalist_ref.outlet }}
                </p>
              </div>
              <div style="display: flex; flex-direction: row; justify-content: flex-end">
                <img
                  v-for="(image, i) in contact.images.slice(0, 3)"
                  class="main-img"
                  :key="i"
                  :src="image"
                  alt=""
                />
                <!-- <img class="main-img" src="" alt="" />
                <img class="main-img" src="" alt="" /> -->
              </div>

              <div
                :class="{ removing: deleting && deletingId === contact.id }"
                @click="openDeleteModal(contact.id)"
                class="absolute-right"
              >
                <img src="@/assets/images/close.svg" height="20px" alt="" />
              </div>
            </header>

            <div style="padding: 0 4px" class="body">
              <div class="bio-text" v-html="contact.bio"></div>
              <!-- <div class="blur"></div> -->
              <div @click="updateContact(contact)" class="more-left">
                Update
                <!-- <img src="@/assets/images/refresh-pr.svg" height="14px" alt="" /> -->
              </div>

              <div @click="setContact(contact)" class="more">
                Expand
                <!-- <img src="@/assets/images/expand-arrows.svg" height="14px" alt="" /> -->
              </div>
            </div>

            <div class="footer">
              <div style="width: 52%" class="rows">
                <div
                  style="padding-right: 10px"
                  v-for="(tag, i) in contact.tags"
                  :key="i"
                  class="user-tag"
                >
                  <img src="@/assets/images/tags.svg" height="12px" alt="" />
                  {{ tag }}
                  <!-- <div @click="modifyTags('remove', tag)" class="remove">
                    <img src="@/assets/images/close.svg" height="14px" alt="" />
                  </div> -->
                </div>
              </div>

              <div style="position: relative" class="row">
                <button
                  @click="showTags(contact, i)"
                  style="padding-left: 8px"
                  class="secondary-button"
                >
                  <img
                    style="margin-right: 2px"
                    src="@/assets/images/add.svg"
                    height="14px"
                    alt=""
                  />
                  Tag
                </button>
                <button @click="openPitchModal(contact)" class="primary-button">Pitch</button>

                <div class="drop-options" v-if="showingTags && currentIndex === i">
                  <header>
                    Apply Tag
                    <img
                      @click="toggleShowTags"
                      src="@/assets/images/close.svg"
                      height="18px"
                      alt=""
                      style="cursor: pointer"
                    />
                  </header>

                  <div style="height: 50px" v-if="!tags.length">You dont have any tags yet...</div>
                  <div
                    style="padding: 0; opacity: 1; height: 120px; overflow: scroll; cursor: text"
                    v-else
                  >
                    <div
                      style="opacity: 1; cursor: text; font-size: 15px"
                      v-for="(tag, i) in tags"
                      :key="i"
                      class="space-between"
                    >
                      {{ tag }}

                      <button
                        :disabled="selectingTag"
                        @click="selectTag(contact, tag, i)"
                        class="tertiary-button"
                      >
                        Select
                      </button>
                    </div>
                  </div>

                  <div style="opacity: 1; cursor: text; position: relative">
                    <div style="opacity: 1" class="sticky-bottom-between">
                      <div
                        style="opacity: 1; margin: 0; cursor: text"
                        v-if="showingInput"
                        class="input-container-small"
                      >
                        <input
                          :disabled="loadingTags"
                          style="
                            border: none;
                            outline: none;
                            padding: 10px 8px 10px 0px;
                            width: 100%;
                          "
                          class="text-area-input"
                          type="text"
                          v-model="newTag"
                          placeholder="Name your tag..."
                        />

                        <img
                          style="filter: invert(40%); margin-right: 20px"
                          src="@/assets/images/user-tag.svg"
                          height="14px"
                          alt=""
                        />
                      </div>

                      <button
                        style="margin-left: auto"
                        v-if="!showingInput"
                        @click="showingInput = true"
                        class="secondary-button"
                      >
                        Create Tag
                      </button>
                      <button
                        :disabled="!newTag || loadingTags"
                        v-if="showingInput"
                        @click="modifyTags('add')"
                        style="margin-bottom: 5px"
                        class="primary-button"
                      >
                        Save
                        <div style="margin-left: 4px" v-if="loadingTags" class="loading-small">
                          <div class="dot"></div>
                          <div class="dot"></div>
                          <div class="dot"></div>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'
import { Comms } from '@/services/comms'
import { quillEditor } from 'vue-quill-editor'
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

export default {
  name: 'Contacts',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    quillEditor,
  },
  data() {
    return {
      newContactImages: [],
      newContactBio: '',
      outletName: '',
      contactName: '',
      orgInfo: '',
      savingContact: false,
      bioModalOpen: false,
      contactsModalOpen: false,
      loadingContacts: false,
      newBio: '',
      newImages: '',
      contactOrg: '',
      detailsModalOpen: false,
      bioLoading: false,
      loading: false,
      currentIndex: 0,
      tagIndex: 0,
      showingInput: false,
      googleModalOpen: false,
      selectingTag: false,
      pitchModalOpen: false,
      currentContact: null,
      showUsers: false,
      selectedUser: null,
      searchUsersText: '',
      searchContactsText: '',
      users: [],
      showList: false,
      contacts: [],
      tagModalOpen: false,
      // 'Test', 'Hello', 'World', 'Tags', 'Will', 'Appear', 'Right Here'
      tags: [],
      newTag: '',
      oldTag: false,
      modifier: 'add',
      selectedTags: [],
      copyTip: 'Copy',
      showingTags: false,
      loadingTags: false,
      subject: '',
      targetEmail: '',
      sendingEmail: false,
      loadingPitch: false,
      revisedPitch: '',
      bccEmail: '',
      showingEditor: false,
      content: '',
      toolbarOptions: [
        ['bold', 'italic', 'underline', 'strike'], // toggled buttons
        ['link'],

        [{ header: 1 }, { header: 2 }], // custom button values
        [{ list: 'ordered' }, { list: 'bullet' }, { list: 'check' }],

        [{ size: ['small', false, 'large', 'huge'] }], // custom dropdown

        ['clean'], // remove formatting button
      ],
      deleting: false,
      deletingId: null,
      deleteModalOpen: false,
      contactId: null,
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    // allUsers() {
    //   return this.users.filter((user) =>
    //     user.full_name.toLowerCase().includes(this.searchUsersText),
    //   )
    // },
    tagCounts() {
      const tagCountMap = {}
      this.tags.forEach((tag) => {
        tagCountMap[tag] = 0
      })

      this.contacts.forEach((contact) => {
        contact.tags.forEach((tag) => {
          if (tagCountMap.hasOwnProperty(tag)) {
            tagCountMap[tag]++
          }
        })
      })

      return Object.keys(tagCountMap).map((tag) => ({
        name: tag,
        count: tagCountMap[tag],
      }))
    },
    filteredContactList() {
      let filteredContacts = this.contacts.filter((contact) => {
        const searchText = this.searchContactsText.toLowerCase()
        // const userFilter = this.userId !== undefined ? this.userId : null
        const userFilter = null
        const tagFilter = this.selectedTags.map((tag) => tag.name.toLowerCase())

        const searchConditions = [
          contact.journalist_ref.first_name.toLowerCase().includes(searchText),
          contact.journalist_ref.last_name.toLowerCase().includes(searchText),
          contact.journalist_ref.email.toLowerCase().includes(searchText),
          contact.journalist_ref.outlet.toLowerCase().includes(searchText),
          contact.bio.toLowerCase().includes(searchText),
          contact.tags.some((tag) => tag.toLowerCase().includes(searchText)),
        ]

        const filterConditions = []

        if (userFilter !== null) {
          filterConditions.push(email.user === userFilter)
        }

        if (tagFilter.length) {
          filterConditions.push(contact.tags.some((tag) => tagFilter.includes(tag.toLowerCase())))
        }

        return (
          searchConditions.some((condition) => condition) &&
          filterConditions.every((condition) => condition)
        )
      })

      return filteredContacts
    },
  },
  watch: {
    tagModalOpen(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.oldTag = false
        this.newTag = ''
      }
    },
    // selectedTags(newVal, oldVal) {
    //   console.log(newVal, oldVal)
    // },
  },
  mounted() {},
  created() {
    this.selectedUser = this.user
    this.bccEmail = this.user.email
    // this.getUsers()
    this.getInitialContacts()
    this.getTags()
  },
  methods: {
    async getJournalistBio() {
      this.newContactBio = ''
      this.newContactImages = []
      this.loadingContacts = true
      try {
        const res = await Comms.api.getJournalistBio({
          journalist: this.contactName,
          outlet: this.outletName,
          content: this.orgInfo,
          search: false,
          social: false,
        })
        const emailRegex = /(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i
        const match = res.data.summary.match(emailRegex)

        if (match) {
          const email = match[1]
          this.targetEmail = email.trim().replace(/\n/g, '')
        }
        this.newContactBio = res.data.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, '')
        this.newContactImages = res.data.images
        this.contactsModalOpen = false
        setTimeout(() => {
          this.bioModalOpen = true
        }, 300)
      } catch (e) {
        console.error(e)
        this.$toast('Error creating bio, please try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loadingContacts = false
      }
    },
    toggleContactsModal() {
      this.contactsModalOpen = !this.contactsModalOpen
    },
    toggleBioModal() {
      this.bioModalOpen = !this.bioModalOpen
    },
    toggleDetailsModal(contact = null) {
      if (contact) {
        this.currentContact = contact
        this.updateContact()
      }
      this.detailsModalOpen = !this.detailsModalOpen
    },
    async saveContact() {
      this.savingContact = true

      try {
        const res = await Comms.api.addContact({
          user: this.user.id,
          email: this.targetEmail,
          journalist: this.contactName,
          bio: this.newContactBio,
          images: this.newContactImages,
          outlet: this.outletName,
        })
        this.$toast('Contact saved!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log('RESPOSNE', e.data.error)
        if (e.data.error.includes('journalist must make a unique set')) {
          this.$toast('Contact is already saved!', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast("Can't verify Journalist", {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        this.savingContact = false
        this.getContacts()
        this.bioModalOpen = false
      }
    },
    async updateContact(contact) {
      this.currentContact = contact
      this.googleModalOpen = true
      this.bioLoading = true
      try {
        const res = await Comms.api.getJournalistBio({
          journalist:
            this.currentContact.journalist_ref.first_name +
            ' ' +
            this.currentContact.journalist_ref.last_name,
          outlet: this.currentContact.journalist_ref.outlet,
          company: 'me',
          search: true,
          social: false,
        })
        this.newBio = res.data.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, '')
        this.newImages = res.data.images
        Comms.api.updateContact({
          id: this.currentContact.id,
          bio: this.newBio,
          images: this.newImages,
        })
        this.$toast('Contact updated!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log('RESPOSNE', e)
        this.$toast('Error updating bio, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.getContacts()
        this.contactOrg = ''
        this.bioLoading = false
        this.googleModalOpen = false
      }
    },
    openDeleteModal(id) {
      this.deleteModalOpen = true
      this.contactId = id
    },
    closeDeleteModal() {
      this.deleteModalOpen = false
    },
    togglePitchModal() {
      this.pitchModalOpen = !this.pitchModalOpen
    },
    openPitchModal(contact) {
      this.googleModalOpen = false
      this.content = ''
      this.revisedPitch = ''
      this.showingEditor = false
      if (contact) {
        this.currentContact = contact
      }

      this.pitchModalOpen = true
    },
    async selectTag(contact, tag, i) {
      this.currentContact = contact
      this.newTag = tag
      this.tagIndex = i
      this.selectingTag = true
      try {
        const res = await Comms.api.modifyTags({
          id: this.currentContact.id,
          tag: this.newTag,
          modifier: this.modifier,
        })
        this.$toast('Tag added', {
          timeout: 1000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        // this.tags = res.results
      } catch (e) {
        console.error(e)
      } finally {
        this.getTags()
        this.getContacts()
        this.selectingTag = false
        this.showingTags = false
      }
    },
    showTags(contact, i) {
      this.showingInput = false
      this.showingInput = false
      this.currentContact = contact
      this.currentIndex = i
      this.showingTags = true
    },
    toggleShowTags() {
      this.showingTags = !this.showingTags
    },
    toggleTagModal() {
      this.tagModalOpen = !this.tagModalOpen
    },
    openTagModal(contact) {
      this.currentContact = contact
      this.tagModalOpen = true
    },
    async sendEmail() {
      this.sendingEmail = true
      try {
        Comms.api
          .sendEmail({
            subject: this.subject,
            body: this.revisedPitch,
            recipient: this.currentContact.journalist_ref.email,
            name:
              this.currentContact.journalist_ref.first_name +
              ' ' +
              this.currentContact.journalist_ref.last_name,
          })
          .then((response) => {
            this.emailJournalistModalOpen = false
            this.$toast('Pitch sent', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.revisedPitch = ''
            this.sendingEmail = false
          })
      } catch (e) {
        console.log(e)
        this.$toast('Error sending email, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.sendingEmail = false
      } finally {
        this.togglePitchModal()
        // this.refreshUser()
      }
    },
    async rewritePitch() {
      this.showingEditor = true
      this.loadingPitch = true
      try {
        const res = await Comms.api.rewritePitch({
          original: this.content,
          bio: this.currentContact.bio,
        })
        // const emailRegex = /email: ([^"]*)/
        // const match = res.pitch.match(emailRegex)
        // if (match) {
        //   const email = match[1]
        //   this.targetEmail = email
        // }
        const body = res.pitch
          .replace(/^Subject(?: Line)?:[\s\S]*?\n/i, '')
          .replace(/email: [^"]*/, '')
        const signature = this.user.emailSignature ? this.user.emailSignature : ''
        const html = `<p>${body.replace(/\n/g, '</p><p>\n')} ${signature.replace(
          /\n/g,
          '</p><p>',
        )}  </p>`
        const quill = this.$refs.quill.quill
        quill.clipboard.dangerouslyPasteHTML(html)
        this.subject = res.pitch.match(/^Subject(?: Line)?:(.*)\n/)[1].trim()

        // this.verifyEmail()
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingPitch = false
      }
    },
    // async verifyEmail() {
    //   this.verifying = true
    //   try {
    //     const res = await Comms.api.verifyEmail({
    //       email: this.targetEmail,
    //       journalist: this.currentJournalist,
    //       publication: this.currentPublication,
    //     })
    //     if (res.data.is_valid) {
    //       setTimeout(() => {
    //         this.emailVerified = true
    //       }, 500)
    //       if (res.data.email) {
    //         this.targetEmail = res.data.email
    //       }
    //     } else {
    //       this.emailError = true
    //     }
    //   } catch (e) {
    //     console.error(e)

    //     this.emailError = true
    //   } finally {
    //     this.refreshUser()
    //     setTimeout(() => {
    //       this.verifying = false
    //     }, 500)
    //   }
    // },
    setContact(contact) {
      this.toggleGoogleModal()
      this.currentContact = contact
    },
    toggleGoogleModal() {
      this.googleModalOpen = !this.googleModalOpen
    },
    async copyBioText() {
      try {
        await navigator.clipboard.writeText(this.currentContact.bio)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    toggleUserDropdown() {
      this.showUsers = !this.showUsers
    },
    toggleListDropdown() {
      this.showList = !this.showList
    },
    // async getUsers() {
    //   try {
    //     const res = await User.api.getAllUsers()
    //     this.users = res.results.filter((user) => user.organization == this.user.organization)
    //     console.log(res)
    //   } catch (e) {
    //     console.log('Error in getTrialUsers', e)
    //   }
    // },
    async getInitialContacts() {
      this.loading = true
      try {
        const res = await Comms.api.getContacts()
        this.contacts = res.results
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async getContacts() {
      try {
        const res = await Comms.api.getContacts()
        this.contacts = res.results
      } catch (e) {
        console.error(e)
      }
    },
    async getTags() {
      try {
        const res = await Comms.api.getContactTagList()
        this.tags = res.tags
      } catch (e) {
        console.error(e)
      }
    },
    async modifyTags(mod, tag) {
      this.loadingTags = true
      try {
        const res = await Comms.api.modifyTags({
          id: this.currentContact.id,
          tag: tag ? tag : this.newTag,
          modifier: mod,
        })
        this.$toast('Tags updated', {
          timeout: 1000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        // this.tags = res.results
      } catch (e) {
        console.error(e)
        this.$toast('Error updating tags, try again', {
          timeout: 1000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.getTags()
        this.getContacts()
        this.loadingTags = false
        this.tagModalOpen = false
        this.showingTags = false
        this.googleModalOpen = false
      }
    },
    async deleteContact(id) {
      this.deletingId = id
      this.deleting = true
      try {
        const res = await Comms.api.deleteContact({
          id: id,
        })
        this.deleteModalOpen = false
        this.$toast('Contact removed', {
          timeout: 1000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        // console.log(res)
      } catch (e) {
        console.error(e)
        this.$toast('Error removing contact', {
          timeout: 1000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.getContacts()
        this.deleting = false
        this.deletingId = null
      }
    },
    clearSearchText() {
      this.searchContactsText = ''
    },
    clearUsersText() {
      this.searchUsersText = ''
    },
    selectUser(user) {
      this.selectedUser = user
      this.toggleUserDropdown()
    },
    selectAllUsers() {
      this.selectedUser = null
      this.toggleUserDropdown()
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.contacts {
  padding: 40px 40px 0 40px;
  font-family: $thin-font-family;
  color: $dark-black-blue;
  overflow: hidden;

  header {
    padding: 24px 0;
  }

  @media only screen and (max-width: 750px) {
    padding: 40px 0;
  }
  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    padding: 40px 16px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.cards-container {
  padding: 16px 0;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 24px;
  height: 75vh;
  overflow: scroll;

  @media only screen and (max-width: 750px) {
    height: 85vh;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.contact-card {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 0 16px;
  width: 25vw;
  background-color: white;
  transition: all 0.5s;
  // height: 200px;

  &:hover {
    .absolute-right {
      visibility: visible;
    }
  }

  .removing {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media only screen and (max-width: 750px) {
    width: 75vw;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 37.5vw;
  }

  .contact-header {
    // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }

  header {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
    padding: 20px 0 16px 0;
    width: 100%;
    border-bottom: 1px solid rgba(0, 0, 0, 0.135);

    .main-img {
      //   margin-right: 16px;
      height: 50px;
      width: 50px;
      //   margin-bottom: 16px;
      object-fit: cover;
      cursor: text;
      border-radius: 8px;
      border: 1px solid rgba(0, 0, 0, 0.1);
    }

    div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 8px;
      overflow: hidden;
      white-space: nowrap;

      img {
        margin-right: 4px;
      }

      p {
        margin: 0;
        font-weight: bold;
        width: 12vw;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
    }

    section {
      font-size: 14px;
    }
  }

  .body {
    line-height: 1.5;
    height: 200px;
    position: relative;
    overflow: hidden;

    p {
      margin: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 14px;
    }
  }

  .body::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 40px;
    // background: linear-gradient(to top, rgba(9, 9, 9, 0.076), rgba(255, 255, 255, 0));
    // filter: blur(2px);
  }

  .footer {
    padding: 16px 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    p {
      margin: 0;
    }
  }

  // &:hover {
  //   box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  //   transform: scale(1.02);
  // }
}

h3 {
  padding: 0;
  margin: 0;
  font-family: $base-font-family;
  font-weight: 400;
}

.more {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: absolute;
  bottom: 4px;
  right: 4px;
  background-color: white;
  z-index: 3;
  font-size: 13px;
  cursor: pointer;
  padding: 3px;
  border: 1px solid rgba(0, 0, 0, 0.285);
  border-radius: 4px;
  box-shadow: 2px 4px 6px 3px rgba(0, 0, 0, 0.1);
  // border-bottom: 1px solid $dark-black-blue;
  transition: all 0.2s;
  &:hover {
    transform: scale(1.075);
  }

  img {
    filter: invert(30%);
  }

  // &:hover {
  //   opacity: 0.9;
  // }
}

.more-left {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: absolute;
  bottom: 4px;
  right: 64px;
  background-color: white;
  z-index: 3;
  font-size: 13px;
  cursor: pointer;
  padding: 3px;
  border: 1px solid rgba(0, 0, 0, 0.285);
  border-radius: 4px;
  box-shadow: 2px 4px 6px 3px rgba(0, 0, 0, 0.1);
  // border-bottom: 1px solid $dark-black-blue;
  transition: all 0.2s;
  &:hover {
    transform: scale(1.075);
  }

  img {
    filter: invert(30%);
  }

  // &:hover {
  //   opacity: 0.9;
  // }
}

.top-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;

  aside {
    width: 19vw;
    padding: 0;
    // background-color: red;

    @media only screen and (max-width: 750px) {
      width: 24vw;
      margin-right: 10px;
      padding-left: 8px;
    }

    @media only screen and (min-width: 751px) and (max-width: 1393px) {
      margin-right: 8px;
    }

    img {
      margin-right: 8px;
      filter: invert(30%);
    }
  }

  section {
    width: 100%;
  }
}

.top-padding {
  padding-top: 8px;
}

.checkbox-list {
  //   max-width: 300px;
  margin: 0 auto;
  padding: 8px 0 20px 0;
  height: 75vh;
  overflow-y: scroll;

  @media only screen and (max-width: 750px) {
    height: 85vh;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    height: 90vh;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
  //   border: 1px solid #e0e0e0;
  //   border-radius: 8px;
  //   background-color: #fff;
}

.checkbox-list ul {
  list-style: none !important;
  padding: 0;
  margin-left: -2px;
  margin: 0;
}

.checkbox-list li {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.checkbox-list label {
  display: flex;
  align-items: center;
  width: 100%;
  font-size: 14px;
  font-family: $base-font-family;
  font-weight: 100;
  letter-spacing: 0.05px;
  opacity: 0.9;
  color: #333;

  @media only screen and (max-width: 750px) {
    font-size: 12px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }

  span {
    font-family: $thin-font-family;

    margin-left: 4px;
  }
}

.checkbox-list input[type='checkbox'] {
  margin-right: 10px;
}

.checkbox-list li:not(:last-child) {
  //   border-bottom: 1px solid #f0f0f0;
}

.custom-checkbox input[type='checkbox'] {
  display: none;
}

/* Create a custom checkbox */
.custom-checkbox .checkmark {
  width: 20px;
  height: 20px;
  border: 1px solid rgba(0, 0, 0, 0.185);
  background-color: white;
  border-radius: 4px;
  display: inline-block;
  position: relative;
  margin-right: 10px;
}

.custom-checkbox input[type='checkbox']:checked + .checkmark {
  background-color: $dark-black-blue; /* Change this to your desired color */
}

.custom-checkbox .checkmark::after {
  content: '';
  position: absolute;
  display: none;
}

.custom-checkbox input[type='checkbox']:checked + .checkmark::after {
  display: block;
}

.custom-checkbox .checkmark::after {
  left: 6px;
  top: 4px;
  width: 2px;
  height: 8px;
  border: 1px solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

h2 {
  margin: 0;
}

.wrapper {
  display: flex;
  align-items: center;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -34px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.search {
  @media only screen and (max-width: 750px) {
    width: 100vw;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 8px 0;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 50vw;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.input {
  position: sticky;
  z-index: 8;
  top: 1.5rem;
  width: 25vw;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.135);
  font-family: $thin-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 12px 20px 12px 10px;

  @media only screen and (max-width: 750px) {
    width: 95%;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 100%;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.pointer {
  cursor: pointer;
}

.relative {
  position: relative;
}
.dropdown {
  position: absolute;
  top: 40px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 8px;
  left: 16px;
  z-index: 6;
  min-width: 25vw;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

  .dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;

    img {
      margin-right: 8px;
    }
  }

  .dropdown-body {
    padding: 0 8px;
    max-height: 250px;
    overflow: scroll;
  }

  .dropdown-item {
    padding: 8px 0;
    cursor: pointer;
    width: 100%;
  }

  .dropdown-item:last-of-type {
    border-bottom: none;
  }

  .dropdown-item:hover {
    opacity: 0.7;
  }

  .dropdown-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 24px 8px 12px 8px;
  }
}

.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  p {
    font-family: $base-font-family;
  }
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.rows {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  width: 80%;
  overflow: scroll;
  scroll-behavior: smooth;
}

.rows::-webkit-scrollbar {
  width: 0px;
  height: 0px;
}

.primary-button {
  @include dark-blue-button();
  border: none;
  border-radius: 16px;

  img {
    filter: invert(100%);
    margin-right: 4px;
  }
}

.secondary-button {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  border-radius: 16px;

  img {
    filter: invert(30%);
  }
}

.tertiary-button {
  @include dark-blue-button();
  background-color: white;
  border: none;
  color: $dark-black-blue;
  padding: 4px;
  &:hover {
    box-shadow: none;
    opacity: 0.5;
  }
}

.no-borders {
  border: none;
  background: transparent;
  margin: 0;
  padding: 0;
  cursor: pointer;

  img {
    transition: all 0.3s;
  }
  img:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: scale(1.075);
  }
}

.red-button {
  @include dark-blue-button();
  border: none;
  color: white;
  background-color: $coral;
  border-radius: 16px;
  margin-left: 16px;
}

.bio-text {
  font-size: 15px;
  line-height: 1.75;
}

::v-deep .bio-text {
  h2 {
    padding: 0;
    margin-bottom: 0 !important;
    margin-block-start: 16px !important;
    margin-block-end: 12px !important;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    line-height: 1;

    font-size: 17px;
  }
}

.base-font {
  font-family: $base-font-family;
}

.bio-modal {
  margin-top: 132px;
  width: 70vw;

  @media only screen and (max-width: 750px) {
    margin-top: 62px;
    width: 90vw;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 85vw;
  }
}

.med-modal {
  width: 55vw !important;
}

.med-container {
  width: 48vw !important;
  padding: 0 16px 0 16px !important;
}

.bio-container {
  width: 60vw;
  max-height: 70vh;
  position: relative;
  overflow-y: scroll;
  color: $base-gray;
  font-family: $thin-font-family;
  padding: 0 24px 0 24px;

  label {
    font-size: 14px;
  }

  @media only screen and (max-width: 750px) {
    width: 85vw;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 75vw;
  }

  header {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    background-color: white;
    padding: 0 0 8px 0;

    p {
      font-weight: bold;
    }
  }

  footer {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    bottom: -1px;
    background-color: white;
    margin: 0;
    padding: 12px 0 0 0;

    .row {
      margin-bottom: 8px;

      .secondary-button {
        margin: 0;
      }
    }
  }

  section {
    padding: 24px 0 16px 0;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    overflow: scroll;

    .bio-body {
      word-wrap: break-word;
      white-space: pre-wrap;
      font-size: 15px;
      overflow: scroll;
    }

    aside {
      display: flex;
      flex-direction: column;
      margin-left: 40px;

      img {
        height: 110px;
        width: 120px;
        margin-bottom: 16px;
        object-fit: cover;
        cursor: text;
        border-radius: 4px;
        border: 1px solid rgba(0, 0, 0, 0.1);
      }
    }
  }
}

::v-deep .bio-body {
  line-height: 1.75 !important;
  padding: 0;
  margin-bottom: 0 !important;
  margin-block-start: 0 !important;
  margin-block-end: 0 !important;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  line-height: 1;

  h2 {
    padding: 0;
    margin-bottom: 0 !important;
    margin-block-start: 8px !important;
    margin-block-end: 0 !important;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    line-height: 1;
  }

  a {
    text-decoration: none;
  }

  strong {
    font-family: $base-font-family;
  }

  ul {
    display: block;
    list-style-type: disc;
    margin-block-start: 0;
    margin-block-end: 0;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    padding-inline-start: 16px;
    unicode-bidi: isolate;
  }

  li {
    margin-top: -32px;
    padding: 0;
  }
}
.wrapper {
  display: flex;
  align-items: center;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip,
.wrapper .tooltip-wide {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -34px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.wrapper .tooltip-below {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  top: 150%;
  color: #fff;
  display: block;
  left: -30px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.tooltip-wide {
  width: 150px !important;
  left: -60px !important;
}

.wrapper .tooltip:before,
.wrapper .tooltip-wide:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip-below:before {
  top: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after,
.wrapper .tooltip-wide:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper .tooltip-below:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-bottom: solid $dark-black-blue 10px;
  top: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip,
.wrapper:hover .tooltip-wide,
.wrapper:hover .tooltip-below {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip,
.lte8 .wrapper .tooltip-wide,
.lt38 .wrapper .tooltip-below {
  display: none;
}

.lte8 .wrapper:hover .tooltip,
.lte8 .wrapper:hover .tooltip-wide,
.lte8 .wrapper:hover .tooltip-below {
  display: block;
}

.icon-button {
  @include dark-blue-button();
  padding: 7px 12px;
  border: 1px solid rgba(0, 0, 0, 0.185);
  img {
    filter: invert(40%);
  }
}

.white-bg {
  background-color: white;
}

.tag-dropdown {
  min-height: 180px;
  margin-top: 20px;
  position: relative;
  display: flex !important;
  flex-direction: column !important;
}

.drop-header {
  padding: 9px 6px;
  background-color: white;
  font-size: 14px !important;
  border: 1px solid rgba(0, 0, 0, 0.185);
  border-radius: 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;

  img {
    margin: 0 8px;
    filter: invert(40%);
  }

  small {
    font-size: 14px;
    margin-left: 4px !important;
    font-family: $base-font-family;
  }
  p {
    font-size: 16px;
  }

  p,
  small {
    margin: 0;
    padding: 0;
  }
}

.drop-options {
  width: 24vw;
  position: absolute;
  bottom: 36px;
  right: -12px;
  font-weight: 400;
  background: white;
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 1000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  div {
    font-size: 14px;
    width: 100%;
    margin-bottom: 6px;
    cursor: pointer;
  }

  header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    padding: 6px 2px 10px 2px;
    margin-bottom: 12px;

    img {
      margin: 0;
    }
  }

  div:hover {
    opacity: 0.55;
  }

  img {
    margin-right: 8px;
  }
}

.input-container-small {
  border: 1px solid rgba(0, 0, 0, 0.185);
  transition: box-shadow 0.3s ease;
  padding: 2px 0;
  border-radius: 9px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  background-color: $off-white;
  margin-top: 16px;

  img {
    filter: invert(40%);
  }

  input {
    background: transparent;
    padding-left: 16px !important;
    font-family: $thin-font-family;
    width: 100%;
  }
}

.text-area-input {
  padding-top: 1rem;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}
.loading-small {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
}
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.user-tag {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 12px;
  background-color: $light-purple;
  color: $grape;
  font-family: $base-font-family;
  font-weight: 100;
  padding: 6px 32px 6px 8px;
  border-radius: 12px;
  img {
    filter: invert(35%) sepia(23%) saturate(810%) hue-rotate(218deg) brightness(93%) contrast(97%);
    margin-right: 4px;
  }

  .remove {
    position: absolute;
    right: 4px;
    top: 6px;
    cursor: pointer;

    &:hover {
      background-color: $grape;
      border-radius: 100%;
      display: flex;
      align-items: center;
      padding: 2px;
      top: 4px;

      img {
        filter: invert(99%);
        margin: 0;
        padding: 0;
      }
    }
  }
}

.sticky-bottom-between {
  position: sticky;
  bottom: 0;
  padding: 0;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  // background-color: red;
}
.area-input {
  width: 100%;
  margin-bottom: 0.25rem;
  max-height: 250px !important;
  padding: 0 1.25rem;
  line-height: 1.25;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  background-color: transparent;
}
.area-input::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.text-area-input {
  padding-top: 1rem;
}

input,
textarea {
  font-family: $thin-font-family;
}

input::placeholder {
  font-family: $thin-font-family;
}
input:disabled {
  cursor: not-allowed;
}
textarea:disabled {
  cursor: not-allowed;
}
textarea::placeholder {
  font-family: $thin-font-family;
}
.e-container {
  background-color: $dark-black-blue;
  color: white;
  border-radius: 6px;
  padding: 4px;
  margin: 0;
  max-width: 240px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.b-container {
  background-color: $white-blue;
  border-radius: 6px;
  padding: 4px 6px;
  margin: 0;
  max-width: 240px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.primary-input-underline {
  width: 100%;
  margin: 1rem 0;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.135);
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 13px;
  padding: 8px 20px 16px 18px;
  outline: none;
}
.primary-input {
  width: 100%;
  margin: 1rem 0;
  border: 1px solid rgba(0, 0, 0, 0.135);
  border-radius: 9px;
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 13px;
  padding: 12px 20px 12px 18px;
  outline: none;
}
.loading-small-absolute {
  position: absolute;
  top: 80%;
  left: 30%;
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
  z-index: 1000;

  p {
    font-size: 16px;
    margin: 0 8px 4px 0;
    padding: 0;
  }
}

.text-editor {
  height: 160px;
  width: 100%;
  border-radius: 8px;

  @media only screen and (max-width: 750px) {
    height: 140px;
  }
}
.green-img {
  img {
    filter: invert(65%) sepia(5%) saturate(4090%) hue-rotate(101deg) brightness(95%) contrast(88%);
    margin-right: 4px;
  }
  color: $dark-green !important;
}

.red-img {
  img {
    filter: invert(46%) sepia(43%) saturate(800%) hue-rotate(308deg) brightness(104%) contrast(97%);
    margin-right: 4px;
  }
  color: $coral !important;
}

.abs-placed {
  position: absolute;
  right: 8px;
  top: 12px;

  p {
    padding: 0;
    margin: 0 4px 0 0;
  }
}
.greenText {
  color: $dark-green !important;
}
.coraltext {
  color: $coral !important;
}
.not-mobile {
  font-family: $thin-font-family;
  font-size: 22px;

  @media only screen and (max-width: 750px) {
    visibility: hidden;
  }
}

.absolute-right {
  position: absolute;
  right: -28px;
  top: -12px;
  background-color: $soft-gray;
  border-radius: 100%;
  padding: 3px 0px 2px 3px;
  cursor: pointer;
  visibility: hidden;

  img {
    // filter: invert(46%) sepia(35%) saturate(2345%) hue-rotate(323deg) brightness(106%) contrast(96%);
    filter: invert(45%);
  }
}

.delete-modal {
  margin-top: 120px;
  width: 100%;
  height: 100%;
}

.delete-container {
  width: 500px;
  height: 220px;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  line-height: 24px;
  font-weight: 400;

  header {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;

    p {
      cursor: pointer;
      margin-top: -24px;
      margin-right: 12px !important;
    }
  }

  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 0.5s forwards;
}
</style>
