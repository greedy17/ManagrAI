<template>
  <div class="contacts fadein">
    <Modal v-if="paidModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Upgrade to Pro</h3>
              <h5 style="margin-top: 12px" class="regen-body-title">
                {{ upgradeMessage }}
              </h5>
            </div>
          </div>
        </div>
        <div style="height: 80px" class="paid-footer">
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="closePaidModal"
            >
              Close
            </div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="googleModalOpen" class="bio-modal">
      <div class="bio-container">
        <header style="border: none">
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
            <div style="margin-left: -32px" class="row">Updated bio will appear here.</div>
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
          <div style="margin-bottom: 8px" class="rows">
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
    <Modal v-if="pitchModalOpen" class="bio-modal">
      <div
        style="
          overflow: hidden;
          padding-left: 12px;
          padding-right: 8px;
          padding-left: 8px;
          padding-bottom: 0;
        "
        class="bio-container"
        :class="{ longmodal: showingEditor && !bulking }"
      >
        <header style="z-index: 10; border: none">
          <p v-if="!bulking" style="font-size: 22px; margin: 8px 0 0 0">
            Pitch
            {{
              currentContact.journalist_ref.first_name +
              ' ' +
              currentContact.journalist_ref.last_name
            }}
          </p>

          <p v-else-if="bulking && !manualBulk" style="font-size: 22px; margin: 8px 0">Auto Pick</p>

          <p v-else style="font-size: 22px; margin: 8px 0">{{ bulkTag }}</p>

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
              :class="{ opaquest: loadingPitch }"
              type="text"
              v-model="content"
              rows="5"
              v-autoresize
              placeholder="Paste your pitch or add company details..."
            />
          </div>
          <div v-if="!bulking" style="font-size: 14px; margin: 12px 0 0 4px" class="row">
            <img src="@/assets/images/profile.svg" height="12px" alt="" />
            <p style="margin: 0 0 0 4px">
              ManagrAI will automatically personalize your pitch based on the Journalist's bio
            </p>
          </div>

          <div
            v-else-if="bulking && !manualBulk"
            style="font-size: 14px; margin: 12px 0 0 4px"
            class="row"
          >
            <img src="@/assets/images/robot.svg" height="12px" alt="" />
            <p style="margin: 0 0 0 4px">
              ManagrAI will generate up to 20 personalized pitches and save them as drafts
            </p>
          </div>

          <div v-else style="font-size: 14px; margin: 12px 0 0 4px" class="row">
            <img src="@/assets/images/adduser.svg" height="12px" alt="" />
            <p style="margin: 0 0 0 4px">
              ManagrAI will generate personalized pitches and save them as drafts
            </p>
          </div>
        </div>

        <div v-if="showingEditor" style="position: relative; margin-top: 12px; margin-bottom: 64px">
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
          </div>

          <!-- :class="{
                coraltext: !currentContact.journalist_ref.verified,
                greenText: currentContact.journalist_ref.verified,
              }" -->

          <div style="position: relative">
            <p
              style="margin: 0; padding: 0; font-size: 18px; position: absolute; left: 0; top: 16px"
            >
              To:
            </p>
            <input
              style="margin-bottom: 0; padding-left: 26px"
              class="primary-input-underline"
              v-model="currentContact.email"
              type="email"
            />

            <!-- <div
              v-if="currentContact.journalist_ref.verified"
              class="row green-img abs-placed"
              style="top: 35%"
            >
              <img src="@/assets/images/shield-check.svg" height="18px" alt="" />
            </div>
            <div v-else class="abs-placed red-img" style="top: 35%">
              <img src="@/assets/images/shield-x.svg" height="14px" alt="" />
            </div> -->
          </div>

          <div style="width: 100%" class="row">
            <div style="position: relative; width: 50%">
              <p
                style="
                  margin: 0;
                  padding: 0;
                  font-size: 18px;
                  position: absolute;
                  left: 0;
                  top: 16px;
                "
              >
                Cc:
              </p>
              <input
                class="primary-input-underline"
                v-model="ccEmail"
                type="text"
                placeholder=""
                style="padding-left: 32px; margin-bottom: 0"
                :disabled="loadingPitch || sendingEmail"
              />
            </div>

            <div style="position: relative; width: 50%">
              <p
                style="
                  margin: 0;
                  padding: 0;
                  font-size: 18px;
                  position: absolute;
                  left: 0;
                  top: 16px;
                "
              >
                Bcc:
              </p>
              <input
                class="primary-input-underline"
                v-model="bccEmail"
                type="text"
                placeholder=""
                style="padding-left: 40px; margin-bottom: 0"
                :disabled="loadingPitch || sendingEmail"
              />
            </div>
          </div>

          <div style="position: relative; margin-bottom: 0">
            <p
              style="margin: 0; padding: 0; font-size: 18px; position: absolute; left: 0; top: 16px"
            >
              Subject:
            </p>
            <input
              class="primary-input-underline"
              v-model="subject"
              type="text"
              placeholder=""
              style="padding-left: 68px"
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
            :class="{ opaquest: loadingPitch || sendingEmail }"
          />

          <div
            v-if="loadingPitch"
            style="margin-left: 12px:font-size:13px"
            class="loading-small-absolute"
          >
            <p>Updating content</p>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>

        <footer>
          <div style="width: 100%" class="row">
            <div style="margin-right: 12px" class="source-dropdown fadein">
              <div
                @click.stop="toggleShowStyles"
                :class="{ 'soft-gray-bg': showingStyles }"
                class="drop-header"
                style="padding-left: 12px"
              >
                <!-- <img src="@/assets/images/wand.svg" height="14px" alt="" /> -->

                <p class="mobile-text-hide">Writing Style:</p>
                <small>{{ writingStyleTitle ? writingStyleTitle : 'Select style' }}</small>
                <img
                  v-if="!showingStyles"
                  src="@/assets/images/arrowDropUp.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else
                  class="rotate-img"
                  src="@/assets/images/arrowDropUp.svg"
                  height="15px"
                  alt=""
                />
              </div>

              <div v-outside-click="hideStyles" v-show="showingStyles" class="drop-options-alt">
                <header style="padding" class="space-between">
                  <h2>Add writing style</h2>
                  <section style="padding: 8px 0" class="h-padding">
                    <section style="padding: 0" @click="toggleStyles" class="toggle">
                      <span :class="{ 'active-toggle': personalStyles }" class="toggle-side">
                        <small>Personal</small>
                      </span>

                      <span :class="{ 'active-toggle': !personalStyles }" class="toggle-side">
                        <small>Group</small>
                      </span>
                    </section>
                  </section>

                  <!-- <button
                    @click="toggleLearnInputModal('')"
                    class="secondary-button-no-border"
                    style="margin-right: 12px"
                  >
                    <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Style
                  </button> -->
                </header>

                <section v-if="userWritingStyles.length">
                  <div
                    @click="addWritingStyle(style.style, style.title)"
                    v-for="style in defaultWritingStyles"
                    :key="style.title"
                    :class="{ activesquare: writingStyleTitle === style.title }"
                    :title="style.title"
                  >
                    <span>
                      <img
                        class="blue-filter"
                        src="@/assets/images/logo.png"
                        height="11px"
                        alt=""
                      />
                      {{ style.title }}
                    </span>
                    <p>{{ style.style }}</p>
                  </div>
                  <div
                    @click="addWritingStyle(style.style, style.title)"
                    class="dropdown-item relative"
                    v-for="(style, i) in userWritingStyles"
                    :key="i"
                    :class="{ activeswitch: writingStyleTitle === style.title }"
                    :title="style.title"
                  >
                    <span class="pink-text">
                      <img
                        class="pink-filter"
                        src="@/assets/images/scroll.svg"
                        height="11px"
                        alt=""
                      />
                      {{ style.title }}
                    </span>
                    <p class="pink-text">{{ style.style }}</p>

                    <!-- <span
                    v-if="hoverIndex === i"
                    @click="deleteWritingStyle(style.id)"
                    class="absolute-icon"
                  >
                    <img src="@/assets/images/close.svg" height="12px" alt="" />
                  </span> -->
                  </div>
                </section>

                <section v-else>
                  <div
                    @click="addWritingStyle(style.style, style.title)"
                    v-for="style in defaultWritingStyles"
                    :key="style.title"
                    :class="{ activeswitch: writingStyleTitle === style.title }"
                  >
                    <span>
                      <img src="@/assets/images/wand.svg" height="11px" alt="" />
                      {{ style.title }}
                    </span>
                    <p>{{ style.style }}</p>
                  </div>
                </section>
              </div>
            </div>

            <div class="source-dropdown fadein">
              <div
                @click.stop="toggleShowDetails"
                :class="{ 'soft-gray-bg': showingDetails }"
                class="drop-header"
                style="padding-left: 12px"
              >
                <!-- <img src="@/assets/images/building.svg" height="14px" alt="" /> -->

                <p class="mobile-text-hide">Company Details:</p>
                <small :title="detailTitle ? detailTitle : 'None'">{{
                  detailTitle ? detailTitle : 'None'
                }}</small>
                <img
                  v-if="!showingDetails"
                  src="@/assets/images/arrowDropUp.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else
                  class="rotate-img"
                  src="@/assets/images/arrowDropUp.svg"
                  height="15px"
                  alt=""
                />
              </div>

              <div
                v-outside-click="hideDetails"
                v-show="showingDetails"
                class="drop-options-alternate"
              >
                <header style="padding-top: 8px; padding-bottom: 8px" class="space-between">
                  <!-- <section class="h-padding">
                    <section>
                      <p style="margin: 0; padding: 4px 0 0 4px; color: #9596b4">Personal</p>
                    </section>
                  </section> -->

                  <!-- <button
                    @click="toggleDetailsInputModal"
                    class="secondary-button-no-border"
                    style="margin-right: 4px"
                  >
                    <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Details
                  </button> -->
                  <h2 style="margin-left: 8px">Add Details</h2>

                  <!-- <button
                  :disabled="!detailTitle"
                  @click="clearDetails"
                  class="secondary-button-no-border borderless"
                >
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/remove.svg"
                    height="14px"
                    alt=""
                  />
                  Clear
                </button> -->
                </header>

                <section v-if="allCompanyDetails.length">
                  <div
                    style="position: relative"
                    @click="addDetails(detail.title, detail.details)"
                    v-for="detail in allCompanyDetails"
                    :key="detail.title"
                    :class="{ activesquareTile: detailTitle === detail.title }"
                    :title="detail.title"
                  >
                    <span class="">
                      <img
                        class="blue-filter"
                        src="@/assets/images/logo.png"
                        height="11px"
                        alt=""
                      />
                      {{ detail.title }}
                    </span>
                    <p class="">{{ detail.details }}</p>

                    <!-- <span @click="deleteCompanyDetails(detail.id)" class="absolute-icon">
                      <img src="@/assets/images/close.svg" height="10px" alt="" />
                    </span> -->
                  </div>
                </section>

                <section style="padding: 16px" v-else>
                  Your saved details
                  <span>
                    <img
                      style="margin-right: 4px"
                      src="@/assets/images/building.svg"
                      height="12px"
                      alt=""
                    />
                    will appear here.</span
                  >
                </section>
              </div>
            </div>
          </div>

          <div style="width: fit-content" class="row">
            <!-- <button class="secondary-button" @click="togglePitchModal">Cancel</button> -->
            <button
              v-if="showingEditor"
              :disabled="loadingPitch || sendingEmail || drafting || !revisedPitch"
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

            <button
              v-if="!showingEditor"
              :disabled="!content || loadingPitch"
              class="primary-button"
              @click="rewritePitch"
              style="width: fit-content; padding: 8px 10px"
            >
              <img
                v-if="loadingPitch"
                style="margin-right: 8px; margin-left: 4px; filter: none"
                class="rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              <span v-if="loadingPitch && bulking">Drafting pitches...</span>
              <span v-else>Continue</span>
            </button>

            <button
              v-else
              :disabled="loadingPitch || sendingEmail || !revisedPitch"
              class="primary-button"
              @click="sendEmail"
            >
              <img
                v-if="sendingEmail"
                style="margin-right: 4px"
                class="invert rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Send Email
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
    <Modal v-if="draftModalOpen" class="delete-modal">
      <div class="delete-container">
        <header style="font-size: 20px" @click="draftModalOpen = false">
          <p>x</p>
        </header>
        <main>
          <div class="row">
            <h2>Successfully created {{ emailCount }} drafts!</h2>
            <img
              class="blue-filter"
              style="margin-left: 8px"
              src="@/assets/images/party-horn.svg"
              height="20px"
              alt=""
            />
          </div>
          <p>Drafts will gradually appear in the Track tab.</p>

          <div style="margin-top: 20px" class="row">
            <button @click="draftModalOpen = false" class="secondary-button">Close</button>
            <button
              style="background-color: #183153; color: white"
              @click="openTracker"
              class="red-button"
            >
              View Drafts
            </button>
          </div>
        </main>
      </div>
    </Modal>

    <Modal class="bio-modal small-modal" v-if="bulkModalOpen">
      <div class="bio-container small-container">
        <header>
          <h2 v-if="!bulkTagging" style="margin: 12px 0">Import Contacts</h2>
          <h2 v-else style="margin: 12px 0">Tag your imported contacts</h2>
        </header>

        <div style="margin-bottom: 16px; height: 300px; width: 100%">
          <ContactMapping
            v-if="!bulkTagging"
            @fieldsFullyMapped="updateMappedField"
          ></ContactMapping>

          <div v-else>
            <div style="margin-top: 16px">
              <h3>Select a tag</h3>
              <div style="height: 50px; margin-top: 32px" v-if="!ExpandedTagList.length">
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
                  margin-bottom: 12px;
                "
                class="scrolltainer"
                v-else
              >
                <div
                  style="
                    opacity: 1;
                    cursor: text;
                    font-size: 15px;
                    padding: 6px 8px;
                    cursor: pointer;
                    border-radius: 4px;
                  "
                  v-for="(tag, i) in ExpandedTagList"
                  @click="selectBulkTag(tag.name)"
                  :key="i"
                  class="space-between hover-bg"
                  :class="{ 'soft-gray-bg': importTag === tag.name }"
                >
                  <div class="row">
                    <img
                      style="margin: 0 8px 0 -4px"
                      src="@/assets/images/tags.svg"
                      height="12px"
                      alt=""
                    />
                    {{ tag.name }}
                  </div>

                  <small v-if="importTag === tag.name">selected</small>
                </div>
              </div>
            </div>

            <div>
              <h3>Create new tag</h3>
              <div style="margin-top: 24px">
                <div style="opacity: 1; margin: 0; cursor: text" class="input-container-small">
                  <input
                    :disabled="loadingTags"
                    style="border: none; outline: none; padding: 10px 8px 10px 0px; width: 100%"
                    class="text-area-input"
                    type="text"
                    @keyup.enter="modifyTagsImport"
                    v-model="importTagName"
                    placeholder="Name your tag..."
                  />

                  <div
                    class="img-container-stay-small"
                    v-if="importTagName"
                    @click="modifyTagsImport"
                    style="margin-right: 12px; padding: 1px 6px 2px 6px"
                  >
                    <img
                      src="@/assets/images/arrow-right.svg"
                      class="pointer"
                      height="10px"
                      alt=""
                    />
                  </div>

                  <img
                    v-else
                    style="filter: invert(40%); margin-right: 20px"
                    src="@/assets/images/tags.svg"
                    height="14px"
                    alt=""
                  />
                </div>

                <div style="margin-top: 16px">
                  <small>To continue without tagging click Import</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <footer>
          <div></div>

          <div class="row">
            <button class="secondary-button" @click="closeBulkModal">Cancel</button>
            <button
              v-if="!bulkTagging"
              class="primary-button"
              :disabled="!mapped"
              @click="toggleBulkTag"
            >
              <img
                v-if="uploading"
                style="margin-right: 4px"
                class="invert rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Continue
            </button>
            <button v-else class="primary-button" :disabled="!mapped" @click="handleFileUpload">
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
          <h2 style="margin: 12px 0">Add Contact</h2>
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
              <img
                v-if="loadingContacts"
                class="rotation"
                style="filter: none"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Continue
            </button>
          </div>
        </footer>
      </div>
    </Modal>

    <Modal class="bio-modal med-modal" v-if="tagModalOpen">
      <div class="bio-container med-container">
        <header>
          <h2 style="margin: 12px 0">Select or Create a Tag</h2>

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
            <h3>Select a tag</h3>
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
                margin-bottom: 12px;
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
                <div class="row">
                  <img
                    style="margin: 0 8px 0 -4px"
                    src="@/assets/images/tags.svg"
                    height="12px"
                    alt=""
                  />
                  {{ tag.name }}
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3>Create a tag</h3>
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

                <div
                  class="img-container-stay-small"
                  v-if="newTag"
                  @click="modifyTags('add')"
                  style="margin-right: 12px; padding: 1px 6px 2px 6px"
                >
                  <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
                </div>

                <img
                  v-else
                  style="filter: invert(40%); margin-right: 20px"
                  src="@/assets/images/tags.svg"
                  height="14px"
                  alt=""
                />
              </div>

              <!-- <button
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
              </button> -->
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
    <!-- <div @click="isDrawerOpen = !isDrawerOpen">TEST</div> -->

    <div class="top-row">
      <section>
        <div style="margin-bottom: 24px" class="space-between">
          <div class="row relative" style="">
            <div
              @click.stop="toggleUserDropdown"
              :class="{ 'soft-gray-bg': showUsers }"
              class="drop-header"
              style="border: none"
            >
              <h3 style="font-size: 14px" class="thin-font row">
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

            <div style="margin-left: 8px" @click="toggleContactsModal" class="icon-btn">
              <img src="@/assets/images/adduser.svg" height="12px" alt="" />
              <div>Add contact</div>
            </div>

            <div style="margin-left: 8px" @click="bulkModalOpen = true" class="icon-btn">
              <img src="@/assets/images/file-import.svg" height="12px" alt="" />
              <div>Import contacts</div>
            </div>

            <div style="position: relative">
              <div style="margin-left: 8px" @click.stop="showBulking = true" class="icon-btn">
                <img src="@/assets/images/users.svg" height="12px" alt="" />
                <div>Bulk pitching</div>
                <img
                  v-if="!showBulking"
                  style="margin-right: -4px; margin-left: 4px"
                  src="@/assets/images/arrowDropUp.svg"
                  height="14px"
                  alt=""
                />
                <img
                  v-else
                  style="margin-right: -4px; margin-left: 4px"
                  class="rotate-img"
                  src="@/assets/images/arrowDropUp.svg"
                  height="14px"
                  alt=""
                />
              </div>

              <div
                v-outside-click="hideBulk"
                v-show="showBulking"
                style="width: 350px"
                class="small-dropdown"
                :class="{ opaquest: loading }"
              >
                <div class="row">
                  <div @click="togglePitchModal(true, isPaid)" class="option fadein">
                    <div class="space-between">
                      <span
                        ><img
                          style="margin-right: 4px"
                          src="@/assets/images/robot.svg"
                          height="12px"
                          alt=""
                        />
                        Auto pick</span
                      >

                      <div class="pro-tag">PRO</div>
                    </div>

                    <p>
                      AI will select up to 20 relevant contacts, then draft personalized pitches.
                    </p>
                  </div>
                  <div
                    @click="toggleBulkTagSelect"
                    class="option fadein"
                    :class="{ outlined: selectingBulkTag }"
                  >
                    <div class="space-between">
                      <span>
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/adduser.svg"
                          height="10px"
                          alt=""
                        />
                        Select manually
                      </span>

                      <div class="pro-tag">PRO</div>
                    </div>

                    <p>
                      Select up to 20 contacts using a Tag. AI will then draft personalized pitches.
                    </p>
                  </div>
                </div>

                <div class="fadein selector" style="width: 100%" v-if="selectingBulkTag">
                  <select style="width: 100%" v-model="bulkTag" class="area-input-outline">
                    <option value="" disabled>Select a Tag</option>
                    <option v-for="(tag, i) in tags" :key="i" :value="tag.name">
                      {{ tag.name }}
                    </option>
                  </select>
                </div>
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
                @keyup.enter="getContactsSearch(false)"
              />

              <div
                class="img-container-stay-small"
                v-if="searchContactsText"
                @click="getContactsSearch(false)"
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
                <td
                  @click="setContact(contact)"
                  style="cursor: pointer"
                  :class="i % 2 !== 0 ? 'gray-bg' : ''"
                >
                  <div class="email-details">
                    <div class="email-info">
                      <div class="subject">
                        {{ contact.outlet ? contact.outlet : contact.journalist_ref.outlet }}
                      </div>
                    </div>
                  </div>
                  <div class="blur"></div>
                </td>
                <td
                  @click="setContact(contact)"
                  style="cursor: pointer"
                  :class="i % 2 !== 0 ? 'gray-bg' : ''"
                  class="set-width"
                >
                  <div style="margin-bottom: 4px; font-size: 14px">
                    {{ contact.journalist_ref.first_name + ' ' + contact.journalist_ref.last_name }}
                  </div>
                </td>
                <td
                  @click="setContact(contact)"
                  style="cursor: pointer"
                  :class="i % 2 !== 0 ? 'gray-bg' : ''"
                >
                  <div class="small-col">
                    {{ contact.email ? contact.email : contact.journalist_ref.email }}
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
                      <img src="@/assets/images/tags.svg" height="12px" alt="" />
                      {{ tag }}
                    </div>
                  </div>
                </td>

                <td :class="i % 2 !== 0 ? 'gray-bg' : ''">
                  <div class="rows">
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
                      @click="openPitchModal(contact)"
                      class="img-container s-wrapper"
                      @mouseenter="showPopover($event, 'Send Email', i)"
                      @mouseleave="hidePopover"
                    >
                      <img
                        style="filter: invert(40%)"
                        src="@/assets/images/email-round.svg"
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
                      @mouseenter="showPopover($event, 'Delete Contact', i)"
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

        <div v-if="processingUpload" class="progress">
          <!---->
          <p>Importing contacts... {{ progressPercentage + '%' }}</p>
          <div class="progress-container">
            <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
          </div>
        </div>

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
              <label :title="tag.name" class="custom-checkbox fadein">
                <input type="checkbox" id="checkbox" :value="tag.name" v-model="selectedTags" />
                <span class="checkmark"></span>
                <div class="ellipsis-text">
                  {{ tag.name }}
                </div>
                <span>({{ tag.count }})</span>
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

    <div v-if="isDrawerOpen" :class="['drawer', { open: isDrawerOpen }]">
      <div class="drawer-header">
        <div style="align-items: flex-start" class="space-between">
          <div>
            <h3 style="font-size: 20px">
              {{
                currentContact.journalist_ref.first_name +
                ' ' +
                currentContact.journalist_ref.last_name
              }}
            </h3>
            <p style="color: #9596b4" class="drawer-header__boldtext">
              {{
                currentContact.outlet ? currentContact.outlet : currentContact.journalist_ref.outlet
              }}
            </p>
          </div>

          <button class="borderless-btn" @click="isDrawerOpen = false">
            <img src="@/assets/images/close.svg" height="18px" alt="" />
          </button>
        </div>

        <div style="width: 90%; overflow-x: scroll; margin: 4px 0 12px 0" class="rows">
          <div
            style="padding-right: 10px"
            v-for="(tag, i) in currentContact.tags"
            :key="i"
            class="user-tag"
          >
            <img src="@/assets/images/tags.svg" height="12px" alt="" />
            {{ tag }}
          </div>
        </div>

        <div class="space-between">
          <div class="nav">
            <p :class="{ activelink: section === 'bio' }" @click="setSection('bio')">Bio</p>
            <p :class="{ activelink: section === 'notes' }" @click="setSection('notes')">Notes</p>
            <p :class="{ activelink: section === 'activity' }" @click="setSection('activity')">
              Activity
            </p>
            <p :class="{ activelink: section === 'insights' }" @click="setSection('insights')">
              AI Insights
            </p>
            <p :class="{ activelink: section === 'edit' }" @click="setSection('edit')">Edit</p>
          </div>

          <div>
            <button
              v-if="section === 'bio'"
              :disabled="bioLoading"
              style="margin: 0"
              class="secondary-button"
              @click="updateContact(currentContact)"
            >
              Refresh bio
            </button>
            <button
              v-else-if="section === 'notes'"
              style="margin: 0"
              class="secondary-button"
              @click="toggleNotes"
            >
              New note
            </button>
            <button
              v-else-if="section === 'insights' && newInsight"
              style="margin: 0"
              class="primary-button"
              @click="clearInsight"
            >
              New insight
            </button>
          </div>
        </div>
      </div>

      <div v-if="section === 'bio'" class="drawer-body fadein">
        <section v-if="!bioLoading">
          <div class="drawer-images" v-if="currentContact.bio">
            <img
              v-for="(url, i) in currentContact.images"
              :key="i"
              :src="`${url}`"
              height="64px"
              alt=""
            />
          </div>

          <div
            v-if="currentContact.bio"
            class="bio-body"
            v-html="currentContact.bio.replace(/<h2>Bio:<\/h2>/g, '')"
          ></div>

          <div style="height: 300px; width: 100%; margin-left: 0" v-else class="bio-body">
            <div class="row">Updated bio will appear here.</div>
          </div>
        </section>

        <section v-else>
          <div style="margin-top: 32px">
            <div class="loading-small">
              <p style="margin-right: 8px">Updating bio</p>
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </section>
      </div>

      <div v-else-if="section === 'notes'" class="drawer-body fadein">
        <section>
          <div class="fadein" v-if="addingNote">
            <textarea
              v-model="newNote"
              rows="5"
              class="area-input text-area-input"
              :class="{ opaquest: loadingPitch }"
              v-autoresize
              placeholder="Add Note..."
              style="
                border: 1px solid rgba(0, 0, 0, 0.1) !important;
                border-radius: 8px;
                padding: 16px 8px;
              "
            ></textarea>
            <div style="margin-top: 8px" class="row-end">
              <button @click="toggleNotes" class="secondary-button">Cancel</button>
              <button :disabled="!newNote" class="primary-button" @click="addNote">Add</button>
            </div>
          </div>

          <div class="fadein" v-else>
            <div v-if="!currentContact.notes || !currentContact.notes.length">
              <div class="row">Notes will appear here.</div>
            </div>

            <div v-else>
              <div
                style="padding-top: 8px; position: relative"
                class="note maxed-height"
                :class="{
                  'maxed-height': !isExpanded[currentContact.notes.length - 1 - i],
                  'expanded-height': isExpanded[currentContact.notes.length - 1 - i],
                  'no-scroll': editingNote[currentContact.notes.length - 1 - i],
                }"
                v-for="(note, i) in currentContact.notes.slice().reverse()"
                :key="i"
              >
                <div class="row">
                  <p class="note__bold">{{ formatDateTime(note.date, false) }}</p>
                </div>

                <p class="note__smaller" v-if="note.modified_by">
                  {{ note.modified_by }} modified on
                  {{ formatDateTime(note.date_modified, true) }}
                </p>

                <p v-else class="note__small">
                  by <span> {{ note.user + '' }}</span>
                </p>

                <p
                  v-if="!editingNote[currentContact.notes.length - 1 - i]"
                  class="pre-text"
                  v-html="note.note"
                ></p>

                <div class="fadein" v-else>
                  <textarea
                    v-model="note.note"
                    rows="5"
                    class="area-input text-area-input"
                    :class="{ opaquest: loadingPitch }"
                    v-autoresize
                    :placeholder="note.note"
                    style="
                      border: 1px solid rgba(0, 0, 0, 0.1) !important;
                      border-radius: 8px;
                      padding: 16px 8px;
                    "
                  ></textarea>
                  <div style="margin-top: 8px" class="space-between">
                    <button
                      @click="deleteNote(currentContact.notes.length - 1 - i)"
                      class="primary-button pinkbg"
                    >
                      Delete
                    </button>

                    <div class="row">
                      <button
                        @click="toggleNoteEdit(currentContact.notes.length - 1 - i)"
                        class="secondary-button"
                      >
                        Cancel
                      </button>
                      <button
                        :disabled="!note.note"
                        class="primary-button"
                        @click="editNote(note.note, currentContact.notes.length - 1 - i)"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                </div>

                <div
                  v-if="!editingNote[currentContact.notes.length - 1 - i]"
                  class="icon-container row"
                >
                  <img
                    src="@/assets/images/edit-note.svg"
                    style="margin-right: 12px"
                    height="14px"
                    alt=""
                    class="expand-icon"
                    @click="toggleNoteEdit(currentContact.notes.length - 1 - i)"
                  />

                  <div
                    style="cursor: pointer"
                    @click="toggleExpand(currentContact.notes.length - 1 - i)"
                  >
                    <img
                      v-if="!isExpanded[currentContact.notes.length - 1 - i]"
                      src="@/assets/images/expanded.svg"
                      height="14px"
                      alt=""
                      class="expand-icon"
                    />
                    <img
                      v-else
                      src="@/assets/images/compress.svg"
                      height="14px"
                      alt=""
                      class="compress-icon"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div v-else-if="section === 'activity'" class="drawer-body fadein">
        <div style="margin-top: 32px" v-if="loadingActivities">
          <div class="loading-small">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>

        <div v-else-if="activities.length">
          <div
            style="padding: 0 0 12px 36px; border: none"
            class="note"
            v-for="(activity, i) in activities"
            :key="i"
          >
            <div class="activity-border">
              <div class="activity-border__img">
                <img
                  v-if="activity.event && activity.event.includes('sent')"
                  src="@/assets/images/email-round.svg"
                  height="12px"
                  alt=""
                />
                <img
                  v-else-if="activity.event && activity.event.includes('open')"
                  src="@/assets/images/envelope-open.svg"
                  height="12px"
                  alt=""
                />
                <img
                  v-else-if="activity.event && activity.event.includes('click')"
                  src="@/assets/images/clicked.svg"
                  height="12px"
                  alt=""
                />
                <img
                  v-else-if="activity.event && activity.event.includes('Approve')"
                  src="@/assets/images/checkbox.svg"
                  height="12px"
                  alt=""
                />
                <img
                  v-else-if="activity.event && activity.event.includes('Reject')"
                  src="@/assets/images/cross-circle.svg"
                  height="12px"
                  alt=""
                />
                <img
                  v-else-if="activity.event && activity.event.includes('draft')"
                  src="@/assets/images/edit-note.svg"
                  height="12px"
                  alt=""
                />
                <img
                  v-else-if="activity.note"
                  src="@/assets/images/note.svg"
                  height="12px"
                  alt=""
                />
              </div>
            </div>

            <p style="margin-top: 0" class="note__bold">
              {{ formatDateTime(activity.date, false) }}
            </p>
            <p class="note__med">
              <span>{{ activity.user ? activity.user + ' ' : '' }}</span>

              <span class="note__small">{{
                activity.event ? formatEvent(activity.event) : activity.note ? 'left a note' : ''
              }}</span>
            </p>
          </div>
        </div>

        <div v-else>
          <div class="row">All activities will appear here.</div>
        </div>
      </div>

      <div v-else-if="section === 'insights'" class="drawer-body fadein">
        <div v-if="!newInsight" class="fadein">
          <textarea
            v-model="insight"
            rows="5"
            class="area-input text-area-input"
            v-autoresize
            placeholder="Ask about recent activity or for suggestions..."
            :class="{ opaquest: loadingInsight }"
            style="
              border: 1px solid rgba(0, 0, 0, 0.1) !important;
              border-radius: 8px;
              padding: 16px 8px;
            "
          ></textarea>

          <div style="margin-top: 8px" class="row-end">
            <!-- <button class="secondary-button">Cancel</button> -->
            <button
              :disabled="!insight || loadingInsight"
              class="primary-button"
              @click="getInsight"
            >
              <img
                v-if="loadingInsight"
                style="margin-right: 8px"
                class="rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Submit
            </button>
          </div>
        </div>

        <div style="overflow-y: scroll" class="fadein" v-else>
          <div class="pre-text" v-html="newInsight"></div>
        </div>
      </div>

      <div v-else-if="section === 'edit'" class="drawer-body fadein">
        <!-- <div class="col">
          <p>First Name</p>
          <input
            class="primary-input"
            v-model="currentContact.journalist_ref.first_name"
            type="text"
          />
        </div>
        <div class="col">
          <p>Last Name</p>
          <input
            class="primary-input"
            v-model="currentContact.journalist_ref.last_name"
            type="text"
          />
        </div> -->
        <div class="col relative">
          <p>Email</p>
          <input
            v-if="currentContact.email"
            @input="updateEmail"
            @keyup.enter="editContact(currentContact.email, '')"
            class="primary-input"
            v-model="currentContact.email"
            type="text"
          />

          <input
            v-else
            @input="updateEmail"
            @keyup.enter="editContact(currentContact.journalist_ref.email, '')"
            class="primary-input"
            v-model="currentContact.journalist_ref.email"
            type="text"
          />
          <img
            v-if="!editingEmail"
            class="abs-placed-img"
            src="@/assets/images/pencil.svg"
            height="14px"
            alt=""
          />

          <div
            class="img-container-stay-small abs-placed-img"
            v-else-if="currentContact.email && editingEmail && !editloading"
            @click="editContact(currentContact.email, '')"
            style="padding: 1px 6px 2px 6px; top: 44px; right: 16px"
          >
            <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
          </div>

          <div
            class="img-container-stay-small abs-placed-img"
            v-else-if="!currentContact.email && editingEmail && !editloading"
            @click="editContact(currentContact.journalist_ref.email, '')"
            style="padding: 1px 6px 2px 6px; top: 44px; right: 16px"
          >
            <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
          </div>

          <img
            v-else-if="editingEmail && editloading"
            class="abs-placed-img rotation"
            src="@/assets/images/loading.svg"
            height="14px"
            alt=""
          />
        </div>

        <div class="col relative">
          <p>Publication</p>

          <input
            v-if="currentContact.outlet"
            @input="updatePub"
            @keyup.enter="editContact('', currentContact.outlet)"
            class="primary-input"
            v-model="currentContact.outlet"
            type="text"
          />

          <input
            v-else
            @input="updatePub"
            @keyup.enter="editContact('', currentContact.journalist_ref.outlet)"
            class="primary-input"
            v-model="currentContact.journalist_ref.outlet"
            type="text"
          />

          <img
            v-if="!editingPub"
            class="abs-placed-img"
            src="@/assets/images/pencil.svg"
            height="14px"
            alt=""
          />

          <div
            class="img-container-stay-small abs-placed-img"
            v-else-if="currentContact.outlet && editingEmail && !editloading"
            @click="editContact('', currentContact.outlet)"
            style="padding: 1px 6px 2px 6px; top: 44px; right: 16px"
          >
            <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
          </div>

          <div
            class="img-container-stay-small abs-placed-img"
            v-else-if="!currentContact.outlet && editingPub && !editloading"
            @click="editContact('', currentContact.journalist_ref.outlet)"
            style="padding: 1px 6px 2px 6px; top: 44px; right: 16px"
          >
            <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
          </div>

          <img
            v-else-if="editingPub && editloading"
            class="abs-placed-img rotation"
            src="@/assets/images/loading.svg"
            height="14px"
            alt=""
          />
        </div>
      </div>
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
      editloading: false,
      editingEmail: false,
      editingPub: false,
      paidModal: false,
      upgradeMessage: '',
      importTagList: [],
      importTagName: '',
      importTag: '',
      bulkTagging: false,
      editingNote: [],
      isExpanded: [],
      newInsight: '',
      loadingInsight: false,
      insight: '',
      loadingActivities: false,
      activities: [],
      newNote: '',
      addingNote: false,
      section: 'bio',
      isDrawerOpen: false,
      currentPublication: '',
      bccEmail: '',
      ccEmail: '',
      manualBulk: false,
      bulkTag: '',
      selectingBulkTag: false,
      emailCount: 0,
      draftModalOpen: false,
      bulking: false,
      showBulking: false,
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
      processingUpload: false,
      progressPercentage: 0,
      currentUser: '',
      showingDetails: false,
      detailTitle: '',
      currentDetails: '',
      allCompanyDetails: [],
      showingStyles: false,
      writingStyleTitle: '',
      personalStyles: true,
      allWritingStyles: [],
      defaultWritingStyles: [
        {
          title: 'Default',
          style: `Begin with a precise introduction, without informal salutations. Be clear, concise, and informative, avoiding metaphors. Offer coherent data without persuasion. Aim for depth, not sensationalism and avoid commercial bias.`,
        },
        {
          title: 'Media Pitch',
          style: `
        1. Start email with "Hi {Journalist first name}", end with "Thanks,". Get right to it, no opening fluff like "I hope this message finds you well"
        2. Tone: Maintain a professional, respectful tone. Show appreciation for the journalist's work and express interest in collaboration.
        3. Formality: Use formal language, but avoid jargon. Keep sentences clear and concise.
        4. Structure: Start with a personalized greeting. Follow with a brief appreciation of the journalist's work, then introduce your topic. Provide key insights, then propose collaboration. End with a forward-looking statement and a thank you.
        5. Linguistic Idiosyncrasies: Use active voice and precise, impactful words. Include statistics and expert opinions for credibility.
        6. Credibility: Establish credibility by referencing recent research, expert opinions, and relevant industry trends.
        7. Engagement: Engage the reader by offering exclusive insights and proposing collaboration.
        8. Non-Promotional: Avoid promotional language. Focus on providing valuable, informative content.
        9. Stylistic Techniques: Use a mix of short and long sentences for rhythm. Use rhetorical questions to engage the reader and provoke thought.
        `,
        },
        {
          title: 'Blog Post',
          style: `The author's style is formal and informative, using a journalistic tone to convey complex scientific concepts in a digestible manner. The structure is linear, starting with historical context and leading to the current developments. The author uses technical jargon, but also provides explanations to ensure understanding. Credibility is established through the mention of renowned scientists, historical achievements, and the university's long-standing involvement in the field. The author avoids persuasive language, focusing on facts and achievements.
        Guidelines: Maintain a formal, journalistic tone. Use technical terms but provide explanations. Structure content linearly, starting with historical context. Establish credibility through mention of renowned figures and achievements. Avoid persuasive language, focusing on facts.`,
        },
        {
          title: 'Email',
          style: `1. Start with a friendly greeting: Use 'Hey' or 'Hi' to initiate a warm, approachable tone.
        2. Be direct and concise: Avoid fluff and unnecessary details. Get straight to the point.
        3. Maintain a neutral tone: Avoid persuasive or sales-oriented language. The tone should be informative, not promotional.
        4. Use simple, clear language: Avoid jargon or complex terms. The goal is to be understood by all readers.
        5. Structure: Use short sentences and paragraphs. Break up information into digestible chunks.
        6. Credibility: Use facts and data to support points. Avoid personal opinions or assumptions.
        7. Action point: End with a clear, actionable step for the reader. This should be direct and easy to understand.
        8. Informality: Maintain a casual, friendly tone throughout. This helps to engage the reader and make the content more relatable.
        9. Linguistic idiosyncrasies: Use common, everyday language. Avoid overly formal or academic language.
        10. Objectivity: Maintain an unbiased stance. Avoid taking sides or expressing personal views.`,
        },
      ],
    }
  },
  computed: {
    searchesUsed() {
      let arr = []
      let currentMonth = new Date(Date.now()).getMonth() + 1
      if (currentMonth < 10) {
        currentMonth = `0${currentMonth}`
      } else {
        currentMonth = `${currentMonth}`
      }
      let currentYear = new Date(Date.now()).getFullYear()
      for (let key in this.$store.state.user.metaData) {
        const item = this.$store.state.user.metaData[key]
        const filteredByMonth = item.timestamps.filter((date) => {
          const split = date.split('-')
          return split[1] == currentMonth && split[0] == currentYear
        })
        arr = [...arr, ...filteredByMonth]
      }
      return arr.length
    },
    ExpandedTagList() {
      return [...this.importTagList, ...this.tags]
    },
    user() {
      return this.$store.state.user
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    allUsers() {
      return this.users.filter((user) =>
        user.full_name.toLowerCase().includes(this.searchUsersText),
      )
    },
    userWritingStyles() {
      if (this.personalStyles) {
        return this.allWritingStyles.filter((style) => style.user === this.user.id)
      } else {
        return this.allWritingStyles
      }
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
        this.getInitialContacts()
      }
    },
    selectedTags(val, oldVal) {
      if (val !== oldVal) {
        this.getContactsSearch(false)
      }
    },
    bulkTag(val, oldVal) {
      if (val !== oldVal) {
        this.getBulkSearch()
      }
    },
  },
  mounted() {
    this.getCompanyDetails()
    this.pitchStyleSetup()
  },
  created() {
    this.selectedUser = this.user
    this.getUsers()
    this.getInitialContacts()
    this.getTags()
    this.getWritingStyles()
  },
  methods: {
    updateEmail() {
      this.editingEmail = true
    },
    updatePub() {
      this.editingPub = true
    },
    async editContact(email, outlet) {
      console.log('here i am test me')
      this.editloading = true
      try {
        const res = await Comms.api.editContact({
          email: email,
          outlet: outlet,
          id: this.currentContact.id,
        })
        console.log(res)
        this.editloading = false
        this.editingEmail = false
        this.editingPub = false
        this.$nextTick(() => {
          this.refreshUser()
          this.getContactsSearch(true)
        })
        this.$toast(`Contact updated`, {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.error(e)
      } finally {
      }
    },
    closeBulkModal() {
      this.bulkModalOpen = false
      this.uploading = false
      this.bulkTagging = false
      this.importTag = ''
      this.importTagList = []
    },
    closePaidModal() {
      this.paidModal = false
    },
    goToContact() {
      window.open('https://managr.ai/contact', '_blank')
    },
    openPaidModal(msg) {
      this.upgradeMessage = msg
      this.paidModal = true
    },
    toggleBulkTag() {
      this.bulkTagging = !this.bulkTagging
    },
    toggleNoteEdit(i) {
      if (this.editingNote[i]) {
        this.$set(this.editingNote, i, false)
        this.toggleExpand(i)
      } else {
        this.$set(this.editingNote, i, true)
        if (!this.isExpanded[i]) {
          this.toggleExpand(i)
        }
      }
    },
    toggleExpand(index) {
      if (this.isExpanded[index]) {
        this.$set(this.isExpanded, index, false)
      } else {
        this.$set(this.isExpanded, index, true)
      }
    },
    clearInsight() {
      this.newInsight = ''
    },
    async getInsight() {
      this.loadingInsight = true
      try {
        const res = await Comms.api.getInsight({
          notes: this.currentContact.notes,
          activity: this.activities,
          bio: this.currentContact.bio,
          instructions: this.insight,
        })
        this.newInsight = res.content.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
      } catch (e) {
        console.error(e)
      } finally {
        this.insight = ''
        this.loadingInsight = false
      }
    },
    formatEvent(txt) {
      if (txt.includes('draft_created')) {
        return 'Email drafted'
      } else if (txt.includes('sent')) {
        return 'sent an email'
      } else {
        return 'Email' + ' ' + txt
      }
    },
    toggleNotes() {
      this.addingNote = !this.addingNote
    },
    formatDateTime(datetimeString, isShort) {
      const date = new Date(datetimeString)
      const timeOptions = {
        hour: 'numeric',
        minute: 'numeric',
        hour12: true,
      }
      const formattedTime = date.toLocaleString('en-US', timeOptions)

      const dateOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }

      const formattedDate = date.toLocaleDateString('en-US', dateOptions)

      if (isShort) {
        return `${formattedDate}`
      } else {
        return `${formattedDate} · ${formattedTime}`
      }
    },
    async addNote() {
      try {
        const res = await Comms.api.addNote({
          id: this.currentContact.id,
          note: this.newNote,
        })
        this.$nextTick(() => {
          this.refreshUser()
          this.getContactsSearch(true)
        })
      } catch (e) {
        console.error(e)
      } finally {
        this.addingNote = false
        this.newNote = ''
      }
    },
    async editNote(note, i) {
      try {
        const res = await Comms.api.editNote({
          id: this.currentContact.id,
          note_index: i,
          note: note,
        })
        console.log(res)
        this.$nextTick(() => {
          this.refreshUser()
          this.getContactsSearch(true)
        })
      } catch (e) {
        console.error(e)
      } finally {
        this.toggleNoteEdit(i)
      }
    },
    async deleteNote(i) {
      try {
        const res = await Comms.api.deleteNote({
          id: this.currentContact.id,
          note_index: i,
        })
        this.$nextTick(() => {
          this.refreshUser()
          this.getContactsSearch(true)
        })
      } catch (e) {
        console.error(e)
      } finally {
        this.toggleNoteEdit(i)
      }
    },
    async getActivities() {
      this.loadingActivities = true
      try {
        const res = await Comms.api.getActivities({
          email: this.currentContact.journalist_ref.email,
        })
        this.activities = res.activity
      } catch (e) {
        console.error(e)
        this.activities = []
      } finally {
        this.refreshUser()
        this.loadingActivities = false
      }
    },
    setSection(name) {
      this.section = name
      if (name === 'activity') {
        this.getActivities()
      }
    },
    toggleBulkTagSelect() {
      if (!this.isPaid) {
        return
      }
      this.selectingBulkTag = !this.selectingBulkTag
    },
    hideBulk() {
      this.showBulking = false
    },
    openTracker() {
      this.$router.push({ name: 'EmailTracking' })
    },
    pitchStyleSetup() {
      const style = `
        1. Start email with "Hi {Journalist first name}", end with "Thanks,". Get right to it, no opening fluff like "I hope this message finds you well"
        2. Tone: Maintain a professional, respectful tone. Show appreciation for the journalist's work and express interest in collaboration.
        3. Formality: Use formal language, but avoid jargon. Keep sentences clear and concise.
        4. Structure: Start with a personalized greeting. Follow with a brief appreciation of the journalist's work, then introduce your topic. Provide key insights, then propose collaboration. End with a forward-looking statement and a thank you.
        5. Linguistic Idiosyncrasies: Use active voice and precise, impactful words. Include statistics and expert opinions for credibility.
        6. Credibility: Establish credibility by referencing recent research, expert opinions, and relevant industry trends.
        7. Engagement: Engage the reader by offering exclusive insights and proposing collaboration.
        8. Non-Promotional: Avoid promotional language. Focus on providing valuable, informative content.
        9. Stylistic Techniques: Use a mix of short and long sentences for rhythm. Use rhetorical questions to engage the reader and provoke thought.
        `
      this.writingStyle = style
      this.writingStyleTitle = 'Media Pitch'
    },
    addWritingStyle(ex, title) {
      this.writingStyle = ex
      this.writingStyleTitle = title
      this.showingStyles = false
      this.showingWritingStyles = false
      if (this.showingEditor) {
        this.rewritePitchWithStyle()
      }
    },
    async getWritingStyles() {
      try {
        await Comms.api
          .getWritingStyles({
            all_styles: false,
          })
          .then((response) => {
            this.allWritingStyles = response
          })
      } catch (e) {}
    },
    toggleStyles() {
      this.personalStyles = !this.personalStyles
    },
    hideStyles() {
      this.showingStyles = false
    },
    toggleShowStyles() {
      if (!this.loadingPitch) {
        this.showingStyles = !this.showingStyles
      }
    },
    addDetails(title, deets) {
      if (title === this.detailTitle) {
        this.detailTitle = ''
        this.content = ''
        this.showingDetails = false
        this.showingAllDetails = false
      }
      this.content = deets
      this.detailTitle = title
      this.showingDetails = false
      this.showingAllDetails = false
      if (this.showingEditor) {
        this.rewritePitch()
      }
    },
    async getCompanyDetails(newDeets = false) {
      try {
        const res = await Comms.api.getCompanyDetails()
        this.allCompanyDetails = res.results
        if (newDeets) {
          let detail = res.results.at(-1)
          this.addDetailsAlt(detail.title, detail.details)
        }
      } catch (e) {}
    },
    clearDetails() {
      this.currentDetails = ''
      this.detailTitle = ''
      this.showingDetails = false
    },
    toggleShowDetails() {
      this.showingDetails = !this.showingDetails
    },
    hideDetails() {
      this.showingDetails = false
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
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
    startProgress() {
      const interval = setInterval(() => {
        if (this.progressPercentage < 100) {
          this.progressPercentage += 10
        } else {
          clearInterval(interval)
          this.processingUpload = false // Optionally hide the progress bar when complete
        }
      }, 1000)
    },
    async processUpload() {
      this.processingUpload = true
      this.startProgress()
      this.checkTasks()
    },
    async checkTasks() {
      try {
        const res = await User.api.checkTasks(this.taskId)
        if (res.completed) {
          this.processingUpload = false
          this.$toast(`Contacts imported successfully!`, {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.refreshUser()
          this.getInitialContacts()
        } else {
          setTimeout(() => {
            this.checkTasks()
          }, 10000)
        }
      } catch (error) {
        console.error(error)
        this.processingUpload = false
        this.$toast('Error updating status, check back later', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async handleFileUpload() {
      this.uploading = true
      try {
        const res = await Comms.api.uploadContacts(
          this.currentFile,
          this.mappings,
          this.sheetName,
          this.importTag,
        )
        this.taskId = res.task_id
        this.$toast(`Processing ${res.num_processing} contacts`, {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.uploading = false
        this.bulkModalOpen = false
        this.processUpload()
        this.uploading = false
        this.bulkTagging = false
        this.importTag = ''
        this.importTagList = []
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
        this.bulkTagging = false
        this.importTag = ''
        this.importTagList = []
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
      if (!this.isPaid && this.searchesUsed >= 20) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }

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
        this.newContactBio = res.data.bio.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        this.newContactImages = res.data.images
        this.currentPublication = res.data.company
        this.targetEmail = res.data.email
        this.contactsModalOpen = false
        this.$nextTick(() => {
          this.refreshUser()
        })
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
          outlet: this.currentPublication,
        })
        this.$toast('Contact saved!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.$nextTick(() => {
          this.refreshUser()
        })
      } catch (e) {
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
        this.getInitialContacts()
        this.bioModalOpen = false
      }
    },
    async updateContact(contact) {
      if (!this.isPaid && this.searchesUsed >= 20) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }
      this.currentContact = contact
      // this.googleModalOpen = true
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

        this.newBio = res.data.bio.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        this.newImages = res.data.images

        Comms.api.updateContact({
          id: this.currentContact.id,
          bio: this.newBio,
          images: this.newImages,
        })
        this.currentContact.bio = this.newBio
        this.currentContact.images = this.newImages
        this.$nextTick(() => {
          this.refreshUser()
        })
        // this.$toast('Contact updated!', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'success',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      } catch (e) {
        this.$toast('Error updating bio, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.contactOrg = ''
        this.bioLoading = false
      }
    },
    openDeleteModal(id) {
      this.deleteModalOpen = true
      this.contactId = id
    },
    closeDeleteModal() {
      this.deleteModalOpen = false
    },
    togglePitchModal(bulk = false, paid = true) {
      if (!paid) {
        return
      }
      this.pitchModalOpen = !this.pitchModalOpen
      if (bulk) {
        this.showBulking = false
        this.bulking = true
      } else {
        this.bulking = false
        this.manualBulk = false
        this.selectingBulkTag = false
      }
    },
    openPitchModal(contact) {
      this.bulking = false
      this.googleModalOpen = false
      this.revisedPitch = ''
      this.showingEditor = false
      this.getContactsSearch(false)
      if (contact) {
        this.currentContact = contact
        this.subject = ''
        this.ccEmail = ''
        this.bccEmail = ''
        this.revisedPitch = this.user.emailSignature ? ` \n${this.user.emailSignature}` : ''
        this.showingEditor = true
      }

      this.pitchModalOpen = true
    },
    selectBulkTag(tag) {
      this.importTag = tag
    },
    async selectTag(tag, i) {
      this.newTag = tag
      this.tagIndex = i
      this.selectingTag = true
      try {
        const res = await Comms.api.modifyTags({
          ids: [this.currentContact.id],
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
        this.getInitialContacts()
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
    async bulkPitch() {
      this.loadingPitch = true
      if (this.manualBulk) {
        this.bulkDraft(this.bulkEmails)
      } else {
        try {
          const res = await Comms.api.getBulkList({
            pitch: this.content,
          })
          const emails = res.data.journalists.map((contact) => contact.email)
          this.bulkDraft(emails)
        } catch (e) {
          this.$toast('Error creating drafts, please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          console.error(e)
          this.loadingPitch = false
        }
      }
    },
    async bulkDraft(emails) {
      try {
        const res = await Comms.api.draftBulkPitches({
          original: this.content,
          style: this.writingStyle,
          emails: emails,
        })
        this.emailCount = emails.length
        this.draftModalOpen = true
        this.loadingPitch = false
        this.togglePitchModal()
      } catch (e) {
        this.$toast('Error creating drafts, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        console.error(e)
        this.loadingPitch = false
      } finally {
        this.bulkEmails = []
        this.manualBulk = false
        this.selectingBulkTag = false
      }
    },
    async sendEmail() {
      this.sendingEmail = true
      try {
        const res = await Comms.api.sendEmail({
          subject: this.subject,
          body: this.revisedPitch,
          recipient: this.currentContact.journalist_ref.email,
          name:
            this.currentContact.journalist_ref.first_name +
            ' ' +
            this.currentContact.journalist_ref.last_name,
          cc: [this.ccEmail],
          bcc: [this.bccEmail],
        })

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
      }
    },
    async rewritePitchWithStyle() {
      this.loadingPitch = true
      try {
        const res = await Comms.api.rewritePitch({
          original: this.content,
          style: this.writingStyle,
          with_style: true,
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
    async rewritePitch() {
      if (this.bulking) {
        this.bulkPitch()
        return
      }
      this.showingEditor = true
      this.loadingPitch = true
      try {
        const res = await Comms.api.rewritePitch({
          original: this.content,
          bio: this.currentContact.bio,
          style: this.writingStyle,
          journalist: this.currentContact.journalist_ref.first_name,
        })
        const body = res.body
        const signature = this.user.emailSignature ? this.user.emailSignature : ''
        const html = `<p>${body.replace(/\n/g, '</p><p>\n')} ${signature.replace(
          /\n/g,
          '</p><p>',
        )}  </p>`
        const quill = this.$refs.quill.quill
        quill.clipboard.dangerouslyPasteHTML(html)
        this.subject = res.subject
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingPitch = false
      }
    },
    setContact(contact) {
      // this.toggleGoogleModal()
      this.isDrawerOpen = !this.isDrawerOpen
      this.section = 'bio'
      this.drafting = false
      this.subject = ''
      this.ccEmail = ''
      this.bccEmail = ''
      this.newInsight = ''
      this.currentContact = contact

      if (this.currentContact && this.currentContact.notes) {
        this.isExpanded = Array(this.currentContact.notes.length).fill(false)
      }

      if (this.currentContact && this.currentContact.notes) {
        this.editingNote = Array(this.currentContact.notes.length).fill(false)
      }

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
    async getBulkSearch() {
      this.loading = true
      try {
        const res = await Comms.api.getContacts({
          search: this.searchContactsText.trim(),
          tags: [this.bulkTag],
          user_id: this.selectedUser ? this.selectedUser.id : null,
        })
        this.bulkEmails = res.results.map((user) => user.journalist_ref.email)
        this.manualBulk = true
        this.togglePitchModal(true, this.isPaid)
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async getContactsSearch(setContact = false) {
      this.loading = true
      try {
        const res = await Comms.api.getContacts({
          search: setContact
            ? this.currentContact.journalist_ref.first_name
            : this.searchContactsText.trim(),
          tags: this.selectedTags,
          user_id: this.selectedUser ? this.selectedUser.id : null,
        })

        if (!setContact) {
          this.allContacts = res.results
          this.contacts = res.results
          this.totalContacts = res.count
          this.previous = res.previous
          this.next = res.next
          this.currentPage = 1

          this.contactsPerPage = this.contacts.length

          const startRange = 1
          const endRange = Math.min(this.contactsPerPage, this.totalContacts)

          this.contactRange = `${startRange}-${endRange} `
        }

        if (setContact) {
          this.currentContact = res.results.filter(
            (contact) => contact.id === this.currentContact.id,
          )[0]
        }
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async loadPage(pageNumber) {
      this.loading = true
      let moreUrl = `jcontact/?page=${pageNumber}`
      if (this.selectedUser) {
        moreUrl += `&user_id=${this.selectedUser.id}`
      }
      try {
        const res = await Comms.api.loadMoreContacts(moreUrl)
        this.allContacts = res.results
        this.contacts = res.results
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
        const res = await Comms.api.getContacts({
          user_id: this.selectedUser ? this.selectedUser.id : null,
        })
        this.allContacts = res.results
        this.contacts = res.results
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

    async getTags() {
      try {
        const res = await Comms.api.getContactTagList()
        this.tags = res.tags
      } catch (e) {
        console.error(e)
      }
    },
    async modifyTagsImport() {
      let newTag = {
        name: this.importTagName,
      }
      this.importTagList.push(newTag)
      this.selectBulkTag(this.importTagName)
      this.importTagName = ''
    },
    async modifyTags(mod, tag) {
      this.loadingTags = true
      try {
        const res = await Comms.api.modifyTags({
          ids: [this.currentContact.id],
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
        this.getContactsSearch()
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
        this.getInitialContacts()
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
      this.getInitialContacts()
      this.toggleUserDropdown()
    },
    selectAllUsers() {
      this.selectedUser = null
      this.getInitialContacts()
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

.pre-text {
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
  color: $dark-black-blue;
  font-family: $thin-font-family;
  font-size: 16px;
  margin-top: 0 !important;
}

::v-deep .pre-text {
  strong,
  h1,
  h2,
  h3 {
    font-family: $base-font-family;
    margin-bottom: 4px;
  }
}

.drawer {
  position: fixed;
  top: 0;
  right: -100%;
  height: 100vh;
  width: 50%;
  background-color: white;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
  z-index: 100;
  transition: right 0.3s ease-in-out;
  padding: 24px 0;

  &.open {
    right: 0;
  }

  // Full width on mobile screens
  @media (max-width: 768px) {
    width: 100%;
  }
}

.borderless-btn {
  border: none;
  padding: 0;
  margin: -4px 0 0 0;
  background-color: transparent;
  cursor: pointer;
}

.drawer-header {
  padding: 56px 24px 12px 16px;
  h2 {
    margin: 0;
  }
  p {
    margin: 8px 0;
  }

  &__boldtext {
    color: $lite-blue;
    font-family: $base-font-family;
    font-size: 14px;
  }

  border-bottom: 1px solid rgba(0, 0, 0, 0.1);

  .nav {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    margin-top: 12px;

    p {
      margin: 8px 32px 0 0;
      cursor: pointer;
      font-size: 15px;
      &:hover {
        opacity: 0.4;
      }
    }
  }
}

.maxed-height {
  height: 112px;
  overflow: hidden;

  &:hover {
    // opacity: 0.8;
  }
}

.no-scroll {
  overflow: hidden !important;
}

.expanded-height {
  height: 258px;
  overflow-y: scroll;
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

.note {
  position: relative;
  padding-bottom: 12px;
  color: $dark-black-blue;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);

  p {
    margin: 8px 0;
  }

  &__bold {
    font-family: $base-font-family;
    font-size: 14px;
  }
  &__small {
    font-size: 13px;
    color: $lite-blue;
    font-family: $base-font-family;
  }
  &__smaller {
    font-size: 13px;
    color: $turq;
    font-family: $base-font-family;
  }
  &__med {
    font-size: 15px;
  }

  transition: max-height 0.3s ease;
}

.note .icon-container {
  position: absolute;
  right: 8px;
  bottom: 8px;
  padding: 2px 8px;
  visibility: hidden;
  transition: visibility 0.1s;
  background-color: white;
}

.note:hover .icon-container {
  visibility: visible;
}

.expand-icon,
.compress-icon {
  cursor: pointer;
}

.activity-border {
  left: 8px;
  height: 100%;
  position: absolute;
  border-left: 2px solid $liter-blue;

  &__img {
    position: absolute;
    background-color: $liter-blue;
    left: -12px;
    top: 0;
    padding: 2px 5px 2px 5px;
    border-radius: 50%;

    img {
      filter: invert(45%) sepia(52%) saturate(1248%) hue-rotate(196deg) brightness(97%)
        contrast(90%) !important;
    }
  }
}

.drawer-body {
  padding: 16px 24px;
  overflow-y: scroll;
  height: 75vh;
  position: relative;
  padding-bottom: 40px;
}

.drawer-images {
  display: flex;
  align-items: center;
  flex-direction: row;
  justify-content: flex-start;
  gap: 12px;
  width: 100%;
  margin-bottom: 12px;
  img {
    border-radius: 4px;
  }
}

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
  margin: 0 2px;
  width: 140px;
  cursor: pointer;
  white-space: nowrap;
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

.activelink {
  font-family: $base-font-family;
  color: $dark-black-blue;
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
  padding: 88px 80px 0 40px;
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

.small-dropdown {
  position: absolute;
  top: 48px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  padding: 8px;
  left: 8px;
  width: 320px;
  border-radius: 4px;
  z-index: 10000;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;

  .option {
    font-size: 13px;
    width: 170px;
    height: 86px;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    font-family: $base-font-family;
    font-weight: 900;
    // overflow: hidden;
    // white-space: nowrap;
    // text-overflow: ellipsis;

    p {
      font-size: 12px !important;
      font-family: $thin-font-family;
      margin: 4px 0 0 0;
      // overflow: hidden;
      // white-space: nowrap;
      // text-overflow: ellipsis;
    }

    &:hover {
      background-color: $soft-gray;
    }
  }

  .selector {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    padding: 8px 0;
  }
}

.area-input-outline {
  width: 300px;
  background-color: $offer-white;
  padding: 5px 8px;
  border-radius: 4px;
  line-height: 1.75;
  border: 1px solid rgba(0, 0, 0, 0.1);
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family;
  font-weight: 400;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;

  resize: none;
}

.outlined {
  border: 1px solid $pinky;
}

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  cursor: pointer;
  background: url('~@/assets/images/downArrow.svg') no-repeat calc(100% - 8px) center;
  background-size: 16px;
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

.ellipsis-text {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.pinkbg {
  background-color: $pinky !important;
  margin: 0;
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
  margin-left: auto;

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
}

.input {
  // position: sticky;
  z-index: 8;
  top: 1.5rem;
  width: 18vw;
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

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  //   width: 50%;
  // }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  // }
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
    margin: 0;
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

.row-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
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
  padding: 8px !important;
  white-space: nowrap;
  width: 100px;

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
  padding: 8px !important;
  white-space: nowrap;
  width: 100px;

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
  margin-top: 56px;
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
  word-wrap: break-word;
  white-space: pre-wrap;
  overflow: scroll;

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

    margin-bottom: 16px !important;
    margin-top: 12px !important;
    font-family: $base-font-family;
    font-size: 19px;
  }

  a {
    text-decoration: none;
    color: $lite-blue;
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
    margin-top: 0;
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
  min-width: 150px;
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
  white-space: nowrap;
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

// .user-tag-purp {
//   position: relative;
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   font-size: 12px;
//   background-color: $grapest;
//   color: $graper;
//   font-family: $base-font-family;
//   padding: 6px 32px 6px 8px;
//   border-radius: 5px;
//   white-space: nowrap;
//   img {
//     filter: invert(51%) sepia(13%) saturate(1063%) hue-rotate(217deg) brightness(96%) contrast(84%);
//     margin-right: 4px;
//   }

//   .remove {
//     position: absolute;
//     right: 4px;
//     top: 6px;
//     cursor: pointer;

//     &:hover {
//       background-color: $graper;
//       border-radius: 100%;
//       display: flex;
//       align-items: center;
//       padding: 2px;
//       top: 4px;

//       img {
//         filter: invert(99%);
//         margin: 0;
//         padding: 0;
//       }
//     }
//   }
// }

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
  margin: 10px 0;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.135);
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 16px;
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

.opaquest {
  opacity: 0.3;
}
.loading-small-absolute {
  position: absolute;
  // background-color: white;
  // border: 0.5px solid rgba(0, 0, 0, 0.15);
  // box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  top: 80%;
  left: 30%;
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 12px 24px;
  z-index: 1000;

  p {
    font-size: 16px;
    margin: 0 8px 4px 0;
    padding: 0;
  }
}

.text-editor {
  height: 35vh;
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

.abs-placed-img {
  position: absolute;
  right: 20px;
  top: 48px;
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
  right: 24px;
  top: 12px;
  border-radius: 100%;
  padding: 7px 8px 4px 8px;
  cursor: pointer;
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

.progress {
  position: fixed;
  bottom: 12px;
  z-index: 1000000;
  width: 20vw;
  padding: 0;

  p {
    font-size: 14px;
    font-family: $base-font-family;
  }
}

.progress-container {
  background-color: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  height: 12px;
  margin: -4px 0 20px 0;
}

.progress-bar {
  height: 100%;
  background-color: $lite-blue;
  transition: width 0.4s ease-in-out;
  border-radius: 8px;
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
  filter: brightness(0) invert(23%) sepia(19%) saturate(984%) hue-rotate(162deg) brightness(92%)
    contrast(87%) !important;
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

::v-deep .ql-toolbar.ql-snow {
  border: none;
  border-radius: 4px;
  padding: 0;
}

::v-deep .ql-container {
  border: none;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  padding: 8px 0 0 0;
  margin-left: -8px;
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

.turq-filter {
  filter: invert(56%) sepia(96%) saturate(331%) hue-rotate(139deg) brightness(90%) contrast(87%);
}
.turq-text {
  color: $turq;
}

.activesquareTile {
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background-color: $soft-gray;
  color: $turq;
  font-family: $base-font-family;
}

.activesquare {
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background-color: $soft-gray;
  color: $dark-black-blue;
  font-family: $base-font-family;
}

.source-dropdown {
  z-index: 1;
  max-width: 50%;
  margin-bottom: 8px;
  p {
    font-size: 14px !important;
  }
  position: relative;

  .drop-header {
    padding: 8px 6px;
    background-color: white;
    font-size: 14px !important;
    border-radius: 16px;
    display: flex;
    flex-direction: row;
    align-items: center;
    cursor: pointer;

    @media only screen and (max-width: 600px) {
      font-size: 12px !important;
    }

    img {
      margin: 0 8px;
      filter: invert(40%);

      @media only screen and (max-width: 600px) {
        // display: none;
      }
    }

    small {
      font-size: 14px;
      margin-left: 4px !important;
      font-family: $base-font-family;
      max-width: 55px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    p,
    small {
      margin: 0;
      padding: 0;
    }

    &:hover {
      background-color: $soft-gray;
    }
  }

  .drop-options-alternate {
    width: 450px;
    max-height: 225px;
    position: absolute;
    bottom: 40px;
    left: -4px;
    font-weight: 400;
    background: white;
    padding: 8px;
    border-radius: 5px;
    font-size: 14px;
    box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
    line-height: 1.5;
    z-index: 1000;
    border: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: flex-start;

    // @media only screen and (max-width: 600px) {
    //   left: -120%;
    //   width: 85vw;
    // }

    section:last-of-type {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 8px;
      overflow-y: scroll;

      &::-webkit-scrollbar {
        width: 4px;
        height: 0px;
      }
      &::-webkit-scrollbar-thumb {
        background-color: $soft-gray;
        box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
        border-radius: 6px;
      }

      &::-webkit-scrollbar-track {
        margin-top: 12px;
      }

      &:hover {
        .absolute-icon {
          visibility: visible;
        }
      }
    }

    div {
      font-size: 14px;
      width: 135px;
      height: 60px;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;

      p {
        font-size: 12px !important;
        font-family: $thin-font-family;
        margin: 4px 0 0 0;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }

      &:hover {
        background-color: $soft-gray;
      }

      span {
        font-family: $base-font-family;
      }
    }

    img {
      margin-right: 4px;
    }
  }

  .drop-options-alt {
    width: 450px;
    max-height: 225px;
    position: absolute;
    bottom: 40px;
    left: -4px;
    font-weight: 400;
    background: white;
    padding: 8px;
    border-radius: 5px;
    font-size: 14px;
    box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
    line-height: 1.5;
    z-index: 1000;
    border: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: flex-start;

    @media only screen and (max-width: 600px) {
      left: -120%;
      width: 85vw;
    }

    section:last-of-type {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 8px;
      overflow-y: scroll;

      &::-webkit-scrollbar {
        width: 4px;
        height: 0px;
      }
      &::-webkit-scrollbar-thumb {
        background-color: $soft-gray;
        box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
        border-radius: 6px;
      }

      &::-webkit-scrollbar-track {
        margin-top: 12px;
      }

      &:hover {
        .absolute-icon {
          visibility: visible;
        }
      }
    }

    div {
      font-size: 14px;
      width: 135px;
      height: 60px;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;

      p {
        font-size: 12px !important;
        font-family: $thin-font-family;
        margin: 4px 0 0 0;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }

      &:hover {
        background-color: $soft-gray;
      }

      span {
        font-family: $base-font-family;
      }
    }

    img {
      margin-right: 4px;
    }
  }

  .drop-options {
    width: 450px;
    position: absolute;
    top: 40px;
    left: 0;
    font-weight: 400;
    background: white;
    padding: 8px;
    border-radius: 5px;
    font-size: 14px;
    box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
    line-height: 1.5;
    z-index: 1000;
    border: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 8px;

    @media only screen and (max-width: 600px) {
      width: 85vw;
      gap: 0px;
    }

    @media only screen and (min-width: 601px) and (max-width: 1250px) {
    }

    div {
      font-size: 14px;
      width: 138px;
      height: 80px;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;

      @media only screen and (max-width: 600px) {
        width: 33.3%;
        white-space: normal;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      p {
        font-size: 11px !important;
        font-family: $thin-font-family;
        margin: 4px 0 0 0;
      }

      &:hover {
        background-color: $soft-gray;
      }

      span {
        font-family: $base-font-family;
      }
    }

    img {
      margin-right: 4px;
    }
  }
}

.rotate-img {
  transform: rotate(180deg);
}
.activeswitch {
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background-color: $soft-gray;
  color: $dark-black-blue;
  font-family: $base-font-family;
  img {
    filter: none;
  }
}

.active-toggle {
  background-color: white;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 3px 11px rgba(0, 0, 0, 0.1);
  padding: 6px 12px;
}

.toggle {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  background-color: $off-white;
  cursor: pointer;
  width: fit-content;
  padding: 2px 1px;
  border-radius: 16px;

  small {
    font-size: 13px;
    margin: 0 4px;
  }
}

.toggle-side {
  width: 80px;
  padding: 6px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.5);
}

.h-padding {
  padding: 8px 12px 16px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pro-tag {
  padding: 3px 4px;
  border-radius: 6px;
  color: white;
  background-color: $pinky;
  font-size: 11px;
}

.longmodal {
  height: 80vh !important;
  min-height: 580px;
}

.paid-modal {
  margin-top: 132px;
  font-family: $thin-font-family;
}

.regen-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  font-family: $thin-font-family;
  // :style="isMobile ? '' : 'width: 610px; min-height: 100px; '"

  @media only screen and (max-width: 600px) {
    font-size: 13px !important;
    width: 100% !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.regen-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid $soft-gray;
  margin-bottom: 1rem;
}
.paid-header {
  position: sticky;
  top: 0;
  background-color: white;
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.regen-header-title {
  font-size: 20px;
  font-family: $base-font-family;
  font-weight: 200;
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 14px;

  margin: 0.5rem 0;
}
.regen-body {
  margin: 0.5rem 0;
  border-bottom: 1px solid $soft-gray;
}
.paid-body {
  margin: 0.5rem 0;
}
.regen-body-title {
  font-size: 14px;
  margin: 0 0 0 0;
}

.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.paid-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  // padding-bottom: 8px;
  margin: 1rem 0 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-button {
  border: 1px solid rgba(0, 0, 0, 0.135) !important;
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}
.save-button {
  @include dark-blue-button();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
</style>
