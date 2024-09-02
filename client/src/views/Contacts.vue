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

          <div class="row">
            <button
              :disabled="bioLoading || loadingTags"
              @click="updateContact(currentContact)"
              class="no-borders s-wrapper"
            >
              <img
                style="filter: invert(40%)"
                src="@/assets/images/refresh-pr.svg"
                height="18px"
                alt=""
              />
              <div class="s-tooltip-below">Update</div>
            </button>
          </div>
        </header>

        <section v-if="!bioLoading">
          <div v-if="currentContact.bio" class="bio-body" v-html="currentContact.bio"></div>

          <div style="height: 300px; width: 100%; margin-left: 0" v-else class="bio-body">
            <div style="margin-left: -32px" class="row">
              Updated bio
              <span>
                <img
                  style="margin-left: 12px; margin-right: -54px"
                  src="@/assets/images/refresh-pr.svg"
                  height="12px"
                  alt=""
              /></span>
              will appear here.
            </div>
          </div>

          <aside v-if="currentContact.bio">
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
              <img class="pink-filter" src="@/assets/images/tags.svg" height="12px" alt="" />
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
      <div style="overflow: hidden" class="bio-container med-container">
        <header style="z-index: 10">
          <p style="font-size: 22px; margin: 8px 0">
            Pitch
            {{
              currentContact.journalist_ref.first_name +
              ' ' +
              currentContact.journalist_ref.last_name
            }}
          </p>

          <!-- <div @click="togglePitchModal">
            <img
              style="cursor: pointer"
              class="right-mar img-highlight"
              src="@/assets/images/close.svg"
              height="18px"
              alt=""
            />
          </div> -->
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
              ManagrAI will automatically personalize your pitch based on the Journalist's bio
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
          <button
            v-if="showingEditor"
            :disabled="loadingPitch || sendingEmail || drafting"
            @click="createDraft"
            class="secondary-button"
          >
            <img
              v-if="drafting"
              style="margin-right: 4px"
              class="invert rotation"
              src="@/assets/images/loading.svg"
              height="14px"
              alt=""
            />
            Save draft
          </button>
          <div v-else></div>

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

    <Modal class="bio-modal small-modal" v-if="bulkModalOpen">
      <div class="bio-container small-container">
        <header>
          <h2 style="margin: 12px 0">Import Contacts</h2>
        </header>

        <div style="margin-bottom: 16px; height: 300px; width: 100%">
          <ContactMapping @fieldsFullyMapped="updateMappedField"></ContactMapping>
        </div>

        <footer>
          <div></div>

          <div class="row">
            <button class="secondary-button" @click="bulkModalOpen = false">Cancel</button>
            <button class="primary-button" :disabled="!mapped" @click="handleFileUpload">
              <img
                v-if="uploading"
                style="margin-right: 4px"
                class="invert rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Import
            </button>
          </div>
        </footer>
      </div>
    </Modal>

    <Modal class="bio-modal med-modal" v-if="contactsModalOpen">
      <div class="bio-container med-container">
        <div class="header">
          <h2 style="margin: 12px 0">Lookup Contact</h2>
          <p>
            ManagrAI will research the contact, offer a real-time bio, and provide pitching tips
          </p>
        </div>

        <div style="margin-top: 16px; margin-bottom: 24px; min-height: 120px; width: 100%">
          <label for="contact">Name</label>
          <input
            :disabled="loadingContacts"
            class="primary-input"
            type="text"
            name="contact"
            v-model="contactName"
          />
          <label for="outlet">Publication</label>
          <input
            :disabled="loadingContacts"
            class="primary-input"
            type="text"
            name="outlet"
            v-model="outletName"
          />
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

    <Modal class="bio-modal med-modal" v-if="tagModalOpen">
      <div class="bio-container med-container">
        <header>
          <h2 style="margin: 12px 0">Apply or Create a Tag</h2>

          <img
            style="cursor: pointer"
            @click="tagModalOpen = false"
            src="@/assets/images/close.svg"
            height="20px"
            alt=""
          />
        </header>

        <div style="margin-top: 16px; margin-bottom: 24px; min-height: 120px; width: 100%">
          <div>
            <h3>Select tag to apply</h3>
            <div style="height: 50px; margin-top: 32px" v-if="!tags.length">
              You dont have any tags yet...
            </div>
            <div
              style="
                padding: 0;
                opacity: 1;
                height: 120px;
                overflow: scroll;
                cursor: text;
                margin-top: 16px;
                margin-bottom: 8px;
              "
              class="scrolltainer"
              v-else
            >
              <div
                style="opacity: 1; cursor: text; font-size: 15px; padding: 5px 8px; cursor: pointer"
                v-for="(tag, i) in tags"
                @click="selectTag(tag.name, i)"
                :key="i"
                class="space-between hover-bg"
              >
                {{ tag.name }}
              </div>
            </div>
          </div>

          <div>
            <h3>Create</h3>
            <div style="margin-top: 24px" class="row">
              <div style="opacity: 1; margin: 0; cursor: text" class="input-container-small">
                <input
                  :disabled="loadingTags"
                  style="border: none; outline: none; padding: 10px 8px 10px 0px; width: 100%"
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
                :disabled="!newTag || loadingTags"
                @click="modifyTags('add')"
                style="margin-bottom: 5px"
                class="primary-button"
              >
                <img
                  v-if="loadingTags"
                  class="rotation"
                  src="@/assets/images/loading.svg"
                  height="14px"
                  alt=""
                />
                Create
              </button>
            </div>
          </div>
        </div>

        <!-- <footer>
          <div></div>
          <div class="row">
            <button class="secondary-button" @click="tagModalOpen = false">Cancel</button>
            <button class="primary-button">Continue</button>
          </div>
        </footer> -->
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

    <div class="top-row">
      <section>
        <!-- <div style="margin-left: -2px; margin-bottom: 24px" class="space-between white-container">
          <div class="row relative" style="padding-bottom: 8px">
            <div
              @click.stop="toggleUserDropdown"
              :class="{ 'soft-gray-bg': showUsers }"
              class="drop-header"
              style="border: none"
            >
              <h3 style="font-size: 16px" class="thin-font row">
                <span class="thin-font-ellipsis"
                  >{{
                    !selectedUser
                      ? 'All'
                      : selectedUser.fullName
                      ? selectedUser.fullName
                      : selectedUser.full_name
                  }}
                </span>
                <span>contacts:</span>
                <div style="margin-left: 8px" v-if="loading" class="loading row">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                <span v-else style="margin-left: 4px">{{ filteredContactList.length }}</span>
              </h3>

              <img
                v-if="!showUsers && !loading"
                style="margin-left: 8px"
                src="@/assets/images/arrowDropUp.svg"
                height="14px"
                alt=""
              />
              <img
                v-else-if="!loading"
                class="rotate-img"
                src="@/assets/images/arrowDropUp.svg"
                height="14px"
                alt=""
              />
            </div>

            <div
              v-outside-click="hideUsers"
              style="left: 0; z-index: 10"
              v-show="showUsers"
              class="dropdown"
            >
              <div class="dropdown-header">
                <h3>Select User</h3>
              </div>

              <div class="dropdown-body">
                <div class="col">
                  <div v-if="!searchUsersText" @click="selectAllUsers" class="dropdown-item">
                    All
                  </div>
                  <div
                    @click="selectUser(user)"
                    class="dropdown-item"
                    v-for="(user, i) in allUsers"
                    :key="i"
                  >
                    {{ user.full_name }}
                  </div>
                </div>
              </div>

              <div class="dropdown-footer"></div>
            </div>

            <div @click="toggleContactsModal" class="icon-btn">
              <img src="@/assets/images/mglass.svg" height="13px" alt="" />
              <div>Lookup contact</div>
            </div>

            <div style="margin-left: 8px" @click="bulkModalOpen = true" class="icon-btn">
              <img src="@/assets/images/file-import.svg" height="14px" alt="" />
              <div>Import contacts</div>
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

              <div
                class="img-container-stay-small"
                v-if="searchContactsText"
                @click="getContactsSearch"
              >
                <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
              </div>
            </div>
          </div>
        </div> -->

        <div style="margin-bottom: 24px" class="space-between">
          <div class="row relative" style="padding-bottom: 8px">
            <div
              @click.stop="toggleUserDropdown"
              :class="{ 'soft-gray-bg': showUsers }"
              class="drop-header"
              style="border: none"
            >
              <h3 style="font-size: 16px" class="thin-font row">
                <img
                  style="margin: 0 4px 0 0"
                  src="@/assets/images/profile.svg"
                  height="12px"
                  alt=""
                />
                User:

                <span style="margin-left: 4px" class="thin-font-ellipsis"
                  >{{
                    !selectedUser
                      ? 'All'
                      : selectedUser.fullName
                      ? selectedUser.fullName
                      : selectedUser.full_name
                  }}
                </span>
              </h3>

              <img
                v-if="!showUsers"
                style="margin-left: 8px"
                src="@/assets/images/arrowDropUp.svg"
                height="14px"
                alt=""
              />
              <img
                v-else
                class="rotate-img"
                src="@/assets/images/arrowDropUp.svg"
                height="14px"
                alt=""
              />
            </div>

            <div
              v-outside-click="hideUsers"
              style="left: 0; z-index: 10"
              v-show="showUsers"
              class="dropdown"
            >
              <div class="dropdown-header">
                <h3>Select User</h3>
              </div>

              <div class="dropdown-body">
                <div class="col">
                  <div v-if="!searchUsersText" @click="selectAllUsers" class="dropdown-item">
                    All
                  </div>
                  <div
                    @click="selectUser(user)"
                    class="dropdown-item"
                    v-for="(user, i) in allUsers"
                    :key="i"
                  >
                    {{ user.full_name }}
                  </div>
                </div>
              </div>

              <div class="dropdown-footer"></div>
            </div>

            <div style="margin-left: 16px" @click="toggleContactsModal" class="icon-btn">
              <img src="@/assets/images/adduser.svg" height="12px" alt="" />
              <div>Add contact</div>
            </div>

            <div style="margin-left: 8px" @click="bulkModalOpen = true" class="icon-btn">
              <img src="@/assets/images/file-import.svg" height="12px" alt="" />
              <div>Import contacts</div>
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
                @keyup.enter="getContactsSearch"
              />

              <div
                class="img-container-stay-small"
                v-if="searchContactsText"
                @click="getContactsSearch"
              >
                <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
              </div>
            </div>
          </div>
        </div>

        <div class="table-border">
          <table>
            <thead>
              <tr style="position: relative">
                <th
                  v-resizableColumn
                  v-for="(value, key) in statsKeys"
                  :key="key"
                  @click="sortBy(value.charAt(0).toLowerCase() + value.slice(1))"
                >
                  {{ value }}

                  <img
                    v-if="
                      sortKey === value.charAt(0).toLowerCase() + value.slice(1) && sortOrder === -1
                    "
                    src="@/assets/images/arrowDrop.svg"
                    height="14px"
                    alt=""
                  />

                  <img
                    v-else-if="
                      sortKey === value.charAt(0).toLowerCase() + value.slice(1) && sortOrder !== -1
                    "
                    src="@/assets/images/arrowDropUp.svg"
                    height="14px"
                    alt=""
                  />

                  <div class="resizer"></div>
                </th>
                <th style="cursor: text" class="mobile-width" v-resizableColumn>
                  Tags
                  <div class="resizer"></div>
                </th>
                <th style="cursor: text" class="mobile-width" v-resizableColumn>
                  Actions
                  <div class="resizer"></div>
                </th>
              </tr>
            </thead>
            <tbody v-if="filteredContactList.length">
              <tr v-for="(contact, i) in filteredContactList" :key="i">
                <td :class="i % 2 !== 0 ? 'gray-bg' : ''" style="cursor: pointer">
                  <div class="email-details">
                    <div class="email-info">
                      <div class="subject">
                        {{ contact.journalist_ref.outlet }}
                      </div>
                    </div>
                  </div>
                  <div class="blur"></div>
                </td>
                <td :class="i % 2 !== 0 ? 'gray-bg' : ''" class="set-width">
                  <div style="margin-bottom: 4px; font-size: 14px">
                    {{ contact.journalist_ref.first_name + ' ' + contact.journalist_ref.last_name }}
                  </div>
                </td>
                <td :class="i % 2 !== 0 ? 'gray-bg' : ''">
                  <div class="small-col">
                    {{ contact.journalist_ref.email }}
                  </div>
                </td>

                <td :class="i % 2 !== 0 ? 'gray-bg' : ''">
                  <div style="width: 160px; overflow: scroll" class="rows">
                    <div
                      style="padding-right: 10px"
                      v-for="(tag, i) in contact.tags"
                      :key="i"
                      class="user-tag"
                    >
                      <img
                        class="pink-filter"
                        src="@/assets/images/tags.svg"
                        height="12px"
                        alt=""
                      />
                      {{ tag }}
                    </div>
                  </div>
                </td>

                <td :class="i % 2 !== 0 ? 'gray-bg' : ''">
                  <div class="rows">
                    <!-- <div
                      @click="openPitchModal(contact)"
                      class="img-container s-wrapper"
                      @mouseenter="showPopover($event, 'Create Pitch', i)"
                      @mouseleave="hidePopover"
                    >
                      <img
                        style="filter: invert(40%)"
                        src="@/assets/images/microphone.svg"
                        height="14px"
                        alt=""
                      />
                    </div> -->

                    <!-- <div
                      @click="updateContact(contact)"
                      class="img-container s-wrapper"
                      @mouseenter="showPopover($event, 'Refresh Bio', i)"
                      @mouseleave="hidePopover"
                    >
                      <img
                        style="filter: invert(40%)"
                        src="@/assets/images/refresh-pr.svg"
                        height="14px"
                        alt=""
                      />
                    </div> -->

                    <div
                      @click="setContact(contact)"
                      class="img-container s-wrapper"
                      @mouseenter="showPopover($event, 'View Bio', i)"
                      @mouseleave="hidePopover"
                    >
                      <img
                        style="filter: invert(40%)"
                        src="@/assets/images/file-user.svg"
                        height="14px"
                        alt=""
                      />
                    </div>

                    <div
                      @click.stop="showTags(contact, i)"
                      class="img-container s-wrapper"
                      @mouseenter="showPopover($event, 'Add Tag', i)"
                      @mouseleave="hidePopover"
                    >
                      <img
                        style="filter: invert(40%)"
                        src="@/assets/images/tags.svg"
                        height="14px"
                        alt=""
                      />
                    </div>

                    <div
                      @click="openDeleteModal(contact.id)"
                      class="img-container s-wrapper"
                      @mouseenter="showPopover($event, 'Delete contact', i)"
                      @mouseleave="hidePopover"
                    >
                      <img
                        class="pink-filter"
                        style="filter: invert(40%)"
                        src="@/assets/images/trash.svg"
                        height="14px"
                        alt=""
                      />
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
            <tbody v-else>
              <div style="margin-top: 16px" v-if="loading" class="loading">
                <div style="margin-left: 16px" class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>

              <div class="mobile-text" style="margin: 16px" v-else>
                Your saved contacts
                <span>
                  <img
                    style="margin-left: 4px; margin-right: 4px"
                    src="@/assets/images/addcontact.svg"
                    height="12px"
                    alt=""
                  />
                  will appear here.</span
                >
              </div>
            </tbody>
          </table>

          <Popover ref="popover">
            {{ popoverContent }}
          </Popover>
        </div>
        <!-- <small v-if="filteredContactList.length" class="smalltxt fadein"
          >list caps at 1,000 contacts</small
        > -->

        <!-- <div class="pagination">
            <div
              @click="onPageClick(page)"
              v-for="(page, i) in pagination"
              :key="i"
              :class="{ 'active-page': currentPage === page }"
            >
              {{ page }}
            </div>
          </div> -->
        <div class="space-between">
          <div></div>

          <div class="pagination-container">
            {{ contactRange }} of {{ totalContacts }}
            <div class="pagination">
              <button
                :disabled="!previous"
                class="no-borders rotate-left"
                @click="loadPage(currentPage - 1)"
              >
                <img
                  :class="{ faded: !previous }"
                  src="@/assets/images/rightarrow.svg"
                  height="16px"
                  alt=""
                />
              </button>

              <button :disabled="!next" class="no-borders" @click="loadPage(currentPage + 1)">
                <img
                  :class="{ faded: !next }"
                  src="@/assets/images/rightarrow.svg"
                  height="16px"
                  alt=""
                />
              </button>
            </div>
          </div>
        </div>
      </section>

      <aside>
        <div style="margin-left: 4px" class="row">
          <img src="@/assets/images/tags.svg" height="14px" alt="" />
          <h3>Tags</h3>
        </div>

        <div class="checkbox-list">
          <ul v-if="tags.length">
            <li v-for="tag in tags" :key="tag.name">
              <label class="custom-checkbox fadein">
                <input type="checkbox" id="checkbox" :value="tag.name" v-model="selectedTags" />
                <span class="checkmark"></span>
                {{ tag.name }} <span>({{ tag.count }})</span>
              </label>
            </li>
          </ul>

          <div v-else-if="loading" class="loading row">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>

          <small v-else> Apply tags to organize journalists into lists. </small>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import Popover from '@/components/Popover.vue'
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
    ContactMapping: () => import(/* webpackPrefetch: true */ '@/components/ContactMapping'),
    Popover,
  },
  data() {
    return {
      contactRange: '',
      totalContacts: null,
      contactsPerPage: null,
      totalPages: null,
      currentPage: null,
      pagination: [],
      next: null,
      previous: null,
      contactCount: 0,
      taskId: '',
      sheetName: '',
      popoverIndex: null,
      popoverContent: '',
      sortOrder: 1,
      sortKey: '',
      statsKeys: ['Publication', 'Name', 'Email'],
      mapped: false,
      isMappingConfirmed: false,
      mappings: {},
      bulkModalOpen: false,
      drafting: false,
      newContactImages: [],
      newContactBio: '',
      outletName: '',
      contactName: '',
      orgInfo:
        'No pitch yet so just base the pitching tips off of what you know of the person and whats available in the prompt.',
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
      allContacts: [],
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
      currentFile: null,
      uploading: false,
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    allUsers() {
      return this.users.filter((user) =>
        user.full_name.toLowerCase().includes(this.searchUsersText),
      )
    },
    // tagCounts() {
    //   const tagCountMap = {}
    //   this.tags.forEach((tag) => {
    //     tagCountMap[tag] = 0
    //   })

    //   this.contacts.forEach((contact) => {
    //     contact.tags.forEach((tag) => {
    //       if (tagCountMap.hasOwnProperty(tag)) {
    //         tagCountMap[tag]++
    //       }
    //     })
    //   })

    //   return Object.keys(tagCountMap).map((tag) => ({
    //     name: tag,
    //     count: tagCountMap[tag],
    //   }))
    // },
    filteredContactList() {
      return this.contacts.slice().sort((a, b) => {
        const aValue =
          this.sortKey === 'publication'
            ? a.journalist_ref.outlet
            : this.sortKey === 'name'
            ? a.journalist_ref.first_name
            : this.sortKey === 'email'
            ? a.journalist_ref.email
            : a[this.sortKey]
        const bValue =
          this.sortKey === 'publication'
            ? b.journalist_ref.outlet
            : this.sortKey === 'name'
            ? b.journalist_ref.first_name
            : this.sortKey === 'email'
            ? b.journalist_ref.email
            : b[this.sortKey]
        if (aValue < bValue) return -1 * this.sortOrder
        if (aValue > bValue) return 1 * this.sortOrder

        return 0
      })
    },
  },
  watch: {
    tagModalOpen(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.oldTag = false
        this.newTag = ''
      }
    },
    searchContactsText(val, oldVal) {
      if (val === '' && oldVal !== '') {
        console.log('from watcher')
        this.getInitialContacts()
      }
    },
    selectedTags(val, oldVal) {
      if (val !== oldVal) {
        this.getContactsSearch()
      }
    },
  },
  created() {
    this.selectedUser = this.user
    this.bccEmail = this.user.email
    this.getUsers()
    this.getInitialContacts()
    this.getTags()
  },
  methods: {
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          // do nothing for now
          return null
        })
    },
    showPopover(event, content, index) {
      this.popoverContent = content
      this.popoverIndex = index
      this.$refs.popover.show(event)
    },
    hidePopover() {
      this.$refs.popover.hide()
      this.popoverIndex = null
    },
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortOrder *= -1
      } else {
        this.sortKey = key
        this.sortOrder = 1
      }
    },
    async handleFileUpload() {
      this.uploading = true
      try {
        const res = await Comms.api.uploadContacts(this.currentFile, this.mappings, this.sheetName)
        console.log(res)
        this.contactCount = res.num_processing
        this.taskId = res.task_id
        this.$toast('Contacts importing! This could take a few minutes.', {
          timeout: 3000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.uploading = false
        this.bulkModalOpen = false
      } catch (error) {
        console.error('Error reading the file:', error)
        this.$toast('Error importing contacts, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.uploading = false
      }
    },
    updateMappedField(mappings, file, name) {
      this.mappings = mappings
      this.currentFile = file
      this.sheetName = name
      this.mapped = true
    },
    async createDraft() {
      this.drafting = true
      try {
        const res = await Comms.api.createDraft({
          subject: this.subject,
          body: this.revisedPitch,
          recipient: this.currentContact.journalist_ref.email,
          name:
            this.currentContact.journalist_ref.first_name +
            ' ' +
            this.currentContact.journalist_ref.last_name,
        })
        this.pitchModalOpen = false
        this.$toast('Draft created', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
        this.$toast('Error creating draft, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.drafting = false
      } finally {
        this.refreshUser()
      }
    },
    hideUsers() {
      this.showUsers = false
    },
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
        const emailRegex = /(?:<strong>\s*Email:\s*<\/strong>|email:\s*|Email:\s*)([^<"\s]+)/i
        const match = res.data.summary.match(emailRegex)

        const companyRegex = /company:\s*([^<]+)/i
        const companyMatch = res.data.summary.match(companyRegex)

        if (companyMatch) {
          const newCompany = companyMatch[1]
          this.currentPublication = newCompany.trim()
        }

        if (match) {
          const email = match[1]
          this.targetEmail = email.trim().replace(/\n/g, '')
        }
        this.newContactBio = res.data.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, '')
          .replace(/company:\s*([^<]+)/i, '')
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
        this.getAllContacts()
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
          .replace(/<h2>Company:<\/h2>\s*<strong>([^<]+)<\/strong>/i, '')

        this.newImages = res.data.images
        Comms.api.updateContact({
          id: this.currentContact.id,
          bio: this.newBio,
          images: this.newImages,
        })
        //     this.$nextTick(() => {

        // })
        this.refreshUser()
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
        this.getAllContacts()
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
    async selectTag(tag, i) {
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
        this.getAllContacts()
        this.selectingTag = false
        this.tagModalOpen = false
      }
    },
    showTags(contact, i) {
      this.showingInput = false
      this.showingInput = false
      this.currentContact = contact
      this.currentIndex = i
      this.tagModalOpen = true
    },
    closeTags() {
      this.showingTags = false
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
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingPitch = false
      }
    },
    setContact(contact) {
      this.toggleGoogleModal()
      this.currentContact = contact

      if (!this.currentContact.bio) {
        this.updateContact(this.currentContact)
      }
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
    async getUsers() {
      try {
        const res = await User.api.getAllUsers()
        this.users = res.results.filter((user) => user.organization == this.user.organization)
      } catch (e) {
        console.log('Error in getTrialUsers', e)
      }
    },
    extractPageFromUrl(url) {
      if (!url) return null
      const apiIndex = url.indexOf('api/')
      if (apiIndex === -1) return null
      return url.substring(apiIndex + 4) // '+ 4' skips the 'api/' part
    },
    async getContactsSearch() {
      console.log(this.selectedTags)
      this.loading = true
      try {
        const res = await Comms.api.getContacts({
          search: this.searchContactsText.trim(),
          tags: this.selectedTags,
        })
        this.allContacts = res.results
        this.contacts = res.results.filter((contact) => contact.user === this.user.id)
        this.totalContacts = res.count
        this.previous = res.previous
        this.next = res.next
        this.currentPage = 1
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async getContactsSearch() {
      console.log(this.selectedTags)
      this.loading = true
      try {
        const res = await Comms.api.getContacts({
          search: this.searchContactsText.trim(),
          tags: this.selectedTags,
        })
        this.allContacts = res.results
        this.contacts = res.results.filter((contact) => contact.user === this.user.id)
        this.totalContacts = res.count
        this.previous = res.previous
        this.next = res.next
        this.currentPage = 1

        // Calculate the number of contacts per page based on the response
        this.contactsPerPage = this.contacts.length

        // Calculate start and end range for the current page
        const startRange = 1
        const endRange = Math.min(this.contactsPerPage, this.totalContacts)

        this.contactRange = `${startRange}-${endRange} `
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async loadPage(pageNumber) {
      this.loading = true
      try {
        const res = await Comms.api.loadMoreContacts(`jcontact/?page=${pageNumber}`)
        this.allContacts = res.results
        this.contacts = res.results.filter((contact) => contact.user === this.user.id)
        this.currentPage = pageNumber
        this.totalContacts = res.count
        this.previous = res.previous
        this.next = res.next

        // Calculate start and end range for the current page
        const startRange = (this.currentPage - 1) * 50 + 1
        const endRange = Math.min(this.currentPage * 50, this.totalContacts)

        this.contactRange = `${startRange}-${endRange}`
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async getInitialContacts() {
      this.loading = true
      try {
        const res = await Comms.api.getContacts()
        this.allContacts = res.results
        this.contacts = res.results.filter((contact) => contact.user === this.user.id)
        this.totalContacts = res.count
        this.contactsPerPage = 50 // Number of contacts per page
        this.currentPage = 1
        this.previous = res.previous
        this.next = res.next

        // Calculate start and end range for the initial page
        const startRange = 1
        const endRange = Math.min(this.contactsPerPage, this.totalContacts)

        this.contactRange = `${startRange}-${endRange}`
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    initializePagination() {
      this.pagination = []

      for (let i = 1; i <= this.totalPages; i++) {
        this.pagination.push(i)
      }
    },
    onPageClick(pageNumber) {
      if (pageNumber !== this.currentPage) {
        this.loadPage(pageNumber)
      }
    },
    async loadNextPage() {
      if (!this.next || this.loading) return

      this.loading = true
      try {
        const res = await Comms.api.loadMoreContacts({ url: this.next })
        this.allContacts = [...this.allContacts, ...res.results]
        console.log(res)
        this.loading = false
        this.next = this.extractPageFromUrl(res.next)
        this.previous = this.extractPageFromUrl(res.previous)

        this.contacts = this.allContacts.filter((contact) => contact.user === this.user.id)
      } catch (e) {
        console.error(e)
      } finally {
      }
    },
    async loadPreviousPage() {
      if (!this.previous) return

      this.loading = true
      try {
        const res = await Comms.api.getContacts({ url: this.previous })
        this.allContacts = [...res.results, ...this.allContacts]

        this.next = this.extractPageFromUrl(res.next)
        this.previous = this.extractPageFromUrl(res.previous)

        this.contacts = this.allContacts.filter((contact) => contact.user === this.user.id)
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async setAllContacts() {
      this.contacts = this.allContacts
    },
    async getAllContacts() {
      let user = this.selectUser
      this.selectUser = ''
      this.selectUser = user
      try {
        const res = await Comms.api.getContacts()
        this.allContacts = res.results
        if (this.selectUser) {
          this.contacts = res.results.filter((contact) => contact.user === this.selectedUser.id)
        } else {
          this.contacts = res.results
        }
      } catch (e) {
        console.error(e)
      }
    },
    async getTags() {
      try {
        const res = await Comms.api.getContactTagList()
        console.log(res)
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
        this
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
        this.getAllContacts()
        this.loadingTags = false
        this.tagModalOpen = false
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
        this.getAllContacts()
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
      this.contacts = this.allContacts.filter((contact) => contact.user === this.selectedUser.id)
      this.toggleUserDropdown()
    },
    selectAllUsers() {
      this.selectedUser = null
      this.setAllContacts()
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

    resizableColumn: {
      bind(el) {
        let startWidth = 0
        let startMouseX = 0
        const minWidth = 75 // Set a reasonable minimum width

        el.addEventListener('mousedown', (e) => {
          if (e.target.classList.contains('resizer')) {
            startWidth = el.offsetWidth
            startMouseX = e.clientX
            document.addEventListener('mousemove', onMouseMove)
            document.addEventListener('mouseup', onMouseUp)
            e.preventDefault()
          }
        })

        function onMouseMove(e) {
          const widthDiff = e.clientX - startMouseX
          const newWidth = startWidth + widthDiff
          if (newWidth > minWidth) {
            el.style.width = `${newWidth}px`
          }
        }

        function onMouseUp() {
          document.removeEventListener('mousemove', onMouseMove)
          document.removeEventListener('mouseup', onMouseUp)
        }
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.skeleton {
  background-color: rgb(236, 236, 236);
  border-radius: 4px;
  margin-bottom: 10px;
  animation: shimmer 3s infinite;
  background: linear-gradient(to right, #dddddde5 8%, #eeeeeef8 18%, #dddddd 33%);
  background-size: 1000px 100%;
}
.skeleton-title {
  height: 20px;
  width: 200px;
}
.skeleton-text {
  height: 20px;
  width: 100%;
}
.skeleton-small {
  height: 20px;
  width: 200px;
}

.skeleton-medium {
  height: 20px;
  width: 70%;
}

.skeleton-large {
  height: 180px;
  width: 100%;
}

@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.scrolltainer {
  &::-webkit-scrollbar {
    width: 5px;
    height: 0px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: $soft-gray;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 6px;
  }
}

.icon-btn {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  padding: 8px 10px;
  margin: 0 10px;
  width: 140px;
  cursor: pointer;
  font-family: $base-font-family;
  img {
    margin-right: 6px;
  }
  &:hover {
    background-color: $soft-gray;
  }
}

.small-col {
  max-width: 200px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pagination-container {
  color: $light-gray-blue;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  border-radius: 4px;
  width: fit-content;
  max-width: 200px;
  margin-top: 12px;
  padding: 8px;
  font-size: 14px;

  span {
    font-family: $base-font-family;
    margin-right: 4px;
  }
}

.rotate-left {
  img {
    transform: rotate(180deg);

    &:hover {
      transform: rotate(180deg);
    }
  }
}

.pagination {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  margin-left: 12px;
}

.active-page {
  font-family: $base-font-family;
  color: $lite-blue;
  background-color: $liter-blue;
}

.smalltxt {
  font-family: $base-font-family;
  margin-top: 12px;
}

.table-border {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  height: 68vh;
  background-color: white;
  overflow: scroll;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;

  tr {
    transition: opacity 1s ease-out;
    opacity: 0;
    animation: fadeIn 1s forwards;
  }

  th,
  td {
    padding: 12px;
    font-size: 15px;
    text-align: left;
    // border-bottom: 1px solid #ddd;
    position: relative;

    .subject,
    .email {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    @media only screen and (max-width: 600px) {
      font-size: 12px;
    }
  }

  thead {
    position: sticky;
    top: 0;
    z-index: 8;
  }

  th {
    background-color: $off-white;
    // font-family: $base-font-family;
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
    color: $dark-blue;
    cursor: pointer;
  }

  td {
    z-index: 1;
    background-color: white;
    overflow: hidden;
  }

  .set-width {
    min-width: 10vw;
    width: 12vw;
  }

  .email-details {
    display: flex;
    align-items: center;
    z-index: 0;
    min-width: 10vw;
    width: 12vw;

    .email-info {
      display: flex;
      flex-direction: column;
      flex-grow: 1;

      .subject {
        font-family: $base-font-family;
        margin-bottom: 4px;
        font-weight: 200;
        font-size: 14px;
        line-height: 24px;
      }

      .email {
        color: gray;
        font-family: $thin-font-family;
        font-size: 14px;
      }
    }
  }
  .resizer {
    width: 10px;
    cursor: col-resize;
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
  }

  .resizer:hover {
    border-right: 1.5px solid $darker-blue;
  }

  .blur {
    width: 12px;
    background: rgba(255, 255, 255, 0.569);
    filter: blur(8px);
    cursor: none;
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
  }

  .relative {
    position: relative;
  }

  .dropdown {
    position: absolute;
    top: 48px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 8px;
    left: 4px;
    // z-index: 4;
    width: 96%;
    min-height: 100px;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

    .dropdown-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      img {
        margin-right: 8px;
      }
    }

    .dropdown-body {
      padding: 0 8px;
    }

    .dropdown-footer {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding: 8px;
    }
  }

  .base-font {
    font-family: $base-font-family;
    font-weight: 200;
    line-height: 24px;
  }

  .dot {
    width: 4px;
    height: 4px;
    margin: 0 6px;
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

  .loading {
    display: flex;
    flex-direction: row;
    align-items: center;
    border-radius: 6px;
    margin-left: 16px;
    padding: 1.5rem 0;

    p {
      margin-right: 8px;
    }
  }

  .stat {
    position: absolute;
    right: 4px;
    top: 14px;
    font-family: $base-font-family;
    font-size: 10px;

    span {
      font-size: 12px;
      padding: 4px 6px;
      border-radius: 11px;
    }

    .red {
      color: $pinky !important;
    }

    .yellow {
      color: $turq !important;
    }

    .green {
      color: $lite-blue !important;
    }
  }
}

.contacts {
  padding: 88px 80px 0 80px;
  font-family: $thin-font-family;
  color: $dark-black-blue;
  overflow: hidden !important;

  header {
    padding: 24px 0;
  }

  @media only screen and (max-width: 600px) {
    padding: 96px 0 48px 0;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    padding: 96px 0 48px 0;
  }
}

.thin-font {
  font-family: $thin-font-family;
}

.thin-font-ellipsis {
  display: inline-block;
  font-family: $thin-font-family;
  overflow: hidden;
  white-space: nowrap;
  max-width: 150px;
  text-overflow: ellipsis;
  margin-right: 4px;
}

.bold-font {
  font-family: $base-font-family;
  color: $dark-black-blue;
  font-weight: 200;
}

.cards-container {
  // background-color: red;
  padding: 16px 0 0 0;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 22px;
  height: 70vh;
  margin-top: 16px;

  overflow: scroll;

  @media only screen and (max-width: 750px) {
    height: 85vh;
    width: 100%;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    height: 78vh;
  }
}

.contact-card {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 0 16px;
  width: 48.3%;
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

  @media only screen and (max-width: 600px) {
    width: 100%;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 48%;
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
      height: 40px;
      width: 40px;
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
    height: 180px;
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
}

h3 {
  padding: 0;
  margin: 0;
  font-family: $base-font-family;
  font-weight: 400;

  span {
    font-family: $base-font-family !important;
  }
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
  padding: 0 24px 0 12px;
  height: 88vh;

  @media only screen and (max-width: 600px) {
    padding: 0;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    padding: 0;
  }

  aside {
    width: 18vw;
    padding: 28px 24px 16px 24px;

    @media only screen and (max-width: 600px) {
      display: none;
    }

    @media only screen and (min-width: 601px) and (max-width: 1024px) {
      padding: 28px 16px 16px 24px;
    }

    img {
      margin-right: 8px;
      filter: invert(30%);
    }
  }

  section {
    width: 99%;
    padding: 16px 16px 16px 32px;

    @media only screen and (max-width: 600px) {
      padding: 16px 8px 16px 12px;
    }

    @media only screen and (min-width: 601px) and (max-width: 1024px) {
      padding: 16px 8px 16px 12px;
    }
  }
}

.checkbox-list {
  //   max-width: 300px;
  margin: 0 auto;
  padding: 16px 0 20px 0;
  height: 80vh;
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
  background-color: $lite-blue;
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

.hover-bg {
  &:hover {
    background-color: $off-white;
    border-radius: 4px;
  }
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.search {
  @media only screen and (max-width: 600px) {
    width: 50vw;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 8px 0;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 50vw;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.input {
  position: sticky;
  z-index: 8;
  top: 1.5rem;
  width: 22vw;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.135);
  font-family: $thin-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 9px 12px 9px 10px;

  @media only screen and (max-width: 600px) {
    width: 95%;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 50%;
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

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotation {
  animation: rotation 2s infinite linear;
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
  // width: 80%;
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

.secondary-button-no-border {
  @include dark-blue-button();
  border-radius: 16px;
  padding: 6px 12px;
  border: none;
  // border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin: 0;
  transition: none;
  font-size: 14px;

  &:hover {
    background-color: $soft-gray !important;
    transform: none !important;
    box-shadow: none;
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
.small-modal {
  width: 40vw !important;

  @media only screen and (max-width: 750px) {
    margin-top: 62px;
    width: 90vw;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 50vw;
  }
}

.med-container {
  width: 48vw !important;
  padding: 0 16px 0 16px !important;
}

.small-container {
  width: 38vw !important;
  padding: 0 16px 0 16px !important;

  @media only screen and (max-width: 750px) {
    width: 90vw;
  }

  @media only screen and (min-width: 751px) and (max-width: 1393px) {
    width: 48vw;
  }
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

  .header {
    h2 {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      background-color: white;
      font-family: $base-font-family;
    }
    position: sticky;
    top: 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    padding: 0 0 8px 0;
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
    font-family: $base-font-family;

    p {
      font-weight: bold;
    }
  }

  footer {
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
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
  padding: 9px 6px 9px 8px;
  background-color: $off-white;
  font-size: 13px !important;
  border: 1px solid rgba(0, 0, 0, 0.185);
  border-radius: 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  // color: $graper;

  &:hover {
    background-color: $soft-gray;
  }

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
  width: 20vw;
  position: absolute;
  bottom: 36px;
  right: 0;
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
    padding: 6px 2px 2px 2px;
    margin-bottom: 12px;
    font-family: $base-font-family;
    font-size: 16px;
    border: none;

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
  background-color: white;
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
  background-color: $liter-blue;
  color: $lite-blue;
  font-family: $base-font-family;
  padding: 6px 32px 6px 8px;
  border-radius: 5px;
  img {
    filter: invert(54%) sepia(16%) saturate(1723%) hue-rotate(159deg) brightness(89%) contrast(89%) !important;
    margin-right: 4px;
  }

  .remove {
    position: absolute;
    right: 4px;
    top: 6px;
    cursor: pointer;

    &:hover {
      background-color: $graper;
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
  background-color: $lite-blue;
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

.faded {
  opacity: 0.2;
  cursor: text;
}

.img-container {
  cursor: pointer;
  padding: 5px 7px 4px 7px;
  border-radius: 50%;
  &:hover {
    background-color: $soft-gray;
  }

  img {
    margin: 0;
    padding: 0;
  }
}

.img-container-stay-small {
  padding: 1px 4px;
  border-radius: 50%;
  background-color: $dark-black-blue;

  img {
    filter: invert(100%);
    margin: 0;
    padding: 0;
  }
}

.img-container-stay {
  padding: 5px 7px 4px 7px;
  border-radius: 50%;
  background-color: $soft-gray;

  img {
    margin: 0;
    padding: 0;
  }
}

.s-tooltip {
  visibility: hidden;
  width: 100px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 10000;
  bottom: 130%;
  left: 50%;
  margin-left: -50px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  // border: 1px solid rgba(0, 0, 0, 0.328);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-tooltip-below {
  visibility: hidden;
  width: 100px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 100%;
  right: 130%;
  margin-top: -28px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-wrapper {
  position: relative;
  display: inline-block;
}

.s-wrapper:hover .s-tooltip,
.s-wrapper:hover .s-tooltip-below {
  visibility: visible;
  opacity: 1;
}

::v-deep ::selection {
  background-color: $lite-blue !important;
  color: white;
}
.lb-text {
  color: $lite-blue;
}
.lb-filter {
  filter: invert(54%) sepia(16%) saturate(1723%) hue-rotate(159deg) brightness(89%) contrast(89%) !important;
}
.blue-filter {
  filter: invert(54%) sepia(16%) saturate(1723%) hue-rotate(159deg) brightness(89%) contrast(89%) !important;
}
.pink-filter {
  filter: invert(43%) sepia(88%) saturate(559%) hue-rotate(280deg) brightness(86%) contrast(83%) !important;
}
.purple-filter {
  filter: invert(51%) sepia(13%) saturate(1063%) hue-rotate(217deg) brightness(96%) contrast(84%);
}

.white-container {
  background-color: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

::v-deep .ql-editor {
  font-family: $thin-font-family;
  font-size: 14px;
}

::v-deep .ql-snow.ql-toolbar button {
  background: $soft-gray;
  border-radius: 4px;
  margin-right: 4px;
}

.soft-gray-bg {
  background-color: $soft-gray;
}

.gray-bg {
  background-color: $off-white !important;
}

.vertical-margin {
  margin: 12px 0;
}
</style>
