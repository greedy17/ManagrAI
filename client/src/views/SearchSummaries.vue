<template>
  <div class="empty-search fadein">
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
              <h5 class="regen-body-title">
                {{ upgradeMessage }}
              </h5>
            </div>
          </div>
        </div>
        <div style="height: 100px" class="paid-footer">
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
    <Modal v-if="successModal" class="paid-modal">
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
              <h3 class="paid-title">Payment Successful!</h3>
              <h5 class="regen-body-title">
                If you have any questions, email us at support@mymanagr.com
              </h5>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="closeSuccessModal"
            >
              Close
            </div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="errorModal" class="paid-modal">
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
              <h3 class="paid-title">Something went wrong</h3>
              <h5 class="regen-body-title">Please try again later.</h5>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="() => (errorModal = false)"
            >
              Close
            </div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="notifyModalOpen" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title">Email Alerts</h4>
            <p class="regen-header-subtitle">
              {{ !alertSet ? 'Select delivery time' : 'Preview your alert' }}
            </p>
          </div>
          <!-- <div class="pointer" @click="toggleNotifyModal"><small>X</small></div> -->
        </div>
        <div class="paid-body">
          <div>
            <div v-if="!alertSet">
              <label for="time-select">Delivery time:</label>
              <input
                id="time-select"
                style="width: 100%; margin-top: 0.5rem"
                class="area-input-outline"
                required
                @input="calculateDate(alertTIme)"
                type="time"
                v-model="alertTIme"
              />
              <small style="font-size: 13px">Recieve a daily email when there is new content</small>
            </div>

            <div class="paid-center" v-else>
              <p>Email Notifications enabled.</p>

              <div class="row">
                <button @click="notifyModalOpen = false" class="secondary-button">Close</button>
                <button class="primary-button" @click="testEmailAlert">Send Preview</button>
              </div>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <div v-if="!alertSet" class="row">
            <button
              style="padding-top: 9px; padding-bottom: 9px; opacity: 1"
              class="cancel-button"
              @click="notifyModalOpen = false"
            >
              Cancel
            </button>
            <button
              @click="addEmailAlert"
              :disabled="savingAlert || !alertTIme"
              class="save-button"
            >
              {{ savingAlert ? 'Submitting' : 'Submit' }}
              <div style="margin-left: 4px" v-if="savingAlert" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="saveModalOpen" class="regen-modal">
      <div :class="{ dim: savingSearch }" class="regen-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">Save</h3>
            <p v-if="mainView === 'write'" class="regen-header-subtitle">Save your Content</p>
            <p v-else-if="mainView === 'discover'" class="regen-header-subtitle">Save your List</p>
            <p v-else class="regen-header-subtitle">Save your current search</p>
          </div>
          <div @click="toggleSaveModal" class="pointer"><small>X</small></div>
        </div>

        <div v-if="mainView === 'write'" class="paid-body">
          <label style="font-size: 13px" for="detail-title">Name</label>
          <input
            id="detail-title"
            style="width: 100%; margin: 0.5rem 0 1rem 0"
            class="area-input-outline"
            type="text"
            placeholder="Name your content..."
            v-model="pitchName"
          />
        </div>

        <div v-else-if="mainView === 'discover'" class="paid-body">
          <label style="font-size: 13px" for="detail-title">Name</label>
          <input
            id="detail-title"
            style="width: 100%; margin: 0.5rem 0 1rem 0"
            class="area-input-outline"
            type="text"
            placeholder="Name your list..."
            v-model="listName"
          />
        </div>

        <div v-else class="paid-body">
          <label style="font-size: 13px" for="detail-title">Name</label>
          <input
            id="detail-title"
            style="width: 100%; margin: 0.5rem 0 1rem 0"
            class="area-input-outline"
            type="text"
            placeholder="Name your search..."
            v-model="searchName"
          />
        </div>

        <div style="margin: 0; padding-bottom: 8px" class="paid-footer aligned-right">
          <div class="row">
            <button :disabled="savingSearch" @click="toggleSaveModal" class="cancel-button">
              Cancel
            </button>

            <!-- <button
              v-if="mainView === 'write'"
              @click="savePitch"
              :disabled="savingSearch"
              class="save-button"
            >
              {{ savingSearch ? 'Saving' : 'Save' }}
              <div style="margin-left: 4px" v-if="savingSearch" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button> -->

            <!-- <button
              v-else-if="mainView === 'discover'"
              @click="saveDiscovery"
              :disabled="savingSearch"
              class="save-button"
            >
              {{ savingSearch ? 'Saving' : 'Save' }}
              <div style="margin-left: 4px" v-if="savingSearch" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button> -->

            <button @click="saveThread" :disabled="savingSearch" class="save-button">
              {{ savingSearch ? 'Saving' : 'Save' }}
              <div style="margin-left: 4px" v-if="savingSearch" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>
    <Modal style="margin-top: 56px" v-if="emailJournalistModalOpen" class="regen-modal">
      <!-- height: 80vh -->
      <div
        style="width: 55vw; min-width: 500px; max-height: 1000px; height: 80vh"
        class="regen-container mobile-min"
      >
        <div style="background-color: white; z-index: 1000" class="paid-header">
          <div class="space-between">
            <h2>Email Pitch</h2>

            <div
              style="padding: 6px 6px 4px 6px"
              @click="toggleEmailJournalistModal"
              class="img-container"
            >
              <img src="@/assets/images/close.svg" height="19px" alt="" />
            </div>
          </div>
        </div>

        <div style="overflow: hidden; height: 80%; margin-top: -12px" class="paid-body">
          <div style="position: relative">
            <div class="row">
              <div
                class="rowed"
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

            <div style="position: relative">
              <p
                class="mobile-top"
                style="
                  margin: 0;
                  padding: 0;
                  font-size: 18px;
                  position: absolute;
                  left: 0;
                  top: 20px;
                "
              >
                To:
              </p>
              <!-- :class="{ coraltext: emailError, greenText: emailVerified }" -->
              <input
                v-if="!verifying || loadingPitch"
                style="margin-bottom: 0; padding-left: 26px; padding-top: 6px"
                class="primary-input-underline"
                v-model="targetEmail"
                type="email"
                :disabled="loadingPitch || sendingEmail || verifying"
              />
              <input
                v-else
                style="margin-bottom: 0; padding-left: 26px"
                class="primary-input-underline"
                type="email"
                :class="{ coraltext: emailError, greenText: emailVerified }"
                disabled
              />

              <!-- <div class="abs-placed row">
                <p @click="showingCc = true" style="margin: 0 8px 0 0; cursor: pointer">Cc</p>
                <p @click="showingBcc = true" style="margin: 0; cursor: pointer">Bcc</p>
              </div> -->
              <div v-if="verifying" style="top: 50%" class="abs-placed loading-small">
                Finding email
                <div style="margin-left: 8px" class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>

              <div v-else-if="emailVerified" class="rowed green-img abs-placed" style="top: 35%">
                <img src="@/assets/images/shield-check.svg" height="18px" alt="" />
              </div>

              <div v-else-if="emailError" class="abs-placed red-img" style="top: 35%">
                <img src="@/assets/images/shield-x.svg" height="14px" alt="" />
              </div>
            </div>

            <div style="width: 100%" class="row">
              <div style="position: relative; width: 50%">
                <p
                  class="mobile-top-s"
                  style="
                    margin: 0;
                    padding: 0;
                    font-size: 18px;
                    position: absolute;
                    left: 0;
                    top: 18px;
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
                  class="mobile-top-s"
                  style="
                    margin: 0;
                    padding: 0;
                    font-size: 18px;
                    position: absolute;
                    left: 0;
                    top: 18px;
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

            <div style="position: relative; margin: 0">
              <p
                style="
                  margin: 0;
                  padding: 0;
                  font-size: 18px;
                  position: absolute;
                  left: 0;
                  top: 20px;
                "
                class="mobile-top"
              >
                Subject:
              </p>
              <input
                class="primary-input-underline"
                v-model="subject"
                type="text"
                placeholder=""
                style="padding-left: 64px; padding-top: 6px"
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

            <div v-if="loadingPitch" style="margin-left: 12px" class="loading-small-absolute">
              <p>Generating email</p>
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </div>

        <div style="position: absolute; bottom: 0" class="space-between">
          <div class="row">
            <div style="margin-top: -4px" class="source-dropdown fadein">
              <div
                @click.stop="toggleShowStylesEmail"
                :class="{ 'soft-gray-bg': showingStylesEmail }"
                class="drop-header"
                style="padding: 8px"
              >
                <img src="@/assets/images/wand.svg" height="14px" alt="" />

                <p class="mobile-text-hide">Voice:</p>
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

              <div
                v-outside-click="hideStylesEmail"
                v-show="showingStylesEmail"
                class="drop-options-alt-up"
              >
                <header class="space-between">
                  <h4>Voices</h4>
                  <p>Select a desired writing style or create your own</p>
                  <!-- <section class="h-padding">
                    <section @click="toggleStyles" class="toggle">
                      <span :class="{ 'active-toggle': personalStyles }" class="toggle-side">
                        <small>Personal</small>
                      </span>

                      <span :class="{ 'active-toggle': !personalStyles }" class="toggle-side">
                        <small>Group</small>
                      </span>
                    </section>
                  </section> -->

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
                    @click="rewritePitchWithStyle(style.style, style.title)"
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
                    @mouseenter="setIndex(i)"
                    @mouseLeave="removeIndex"
                    @click="rewritePitchWithStyle(style.style, style.title)"
                    class="dropdown-item relative"
                    v-for="(style, i) in userWritingStyles"
                    :key="i"
                    :class="{ activeswitch: writingStyleTitle === style.title }"
                    :title="style.title"
                  >
                    <span>
                      {{ style.title }}
                    </span>
                    <p>{{ style.style }}</p>

                    <span
                      v-if="hoverIndex === i"
                      @click="deleteWritingStyle(style.id)"
                      class="absolute-icon"
                    >
                      <img src="@/assets/images/close.svg" height="12px" alt="" />
                    </span>
                  </div>
                </section>

                <section v-else>
                  <div
                    @click="rewritePitchWithStyle(style.style, style.title)"
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

            <div style="margin-top: -4px; margin-left: 8px" class="source-dropdown fadein">
              <div
                @click.stop="toggleShowDetailsEmail"
                :class="{ 'soft-gray-bg': showingDetailsEmail }"
                class="drop-header"
                style="padding: 8px"
              >
                <img src="@/assets/images/folder.svg" height="14px" alt="" />

                <p class="mobile-text-hide">Project:</p>
                <small :title="detailTitle ? detailTitle : 'None'">{{
                  detailTitle ? detailTitle : 'None'
                }}</small>
                <img
                  v-if="!showingDetailsEmail"
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
                v-outside-click="hideDetailsEmail"
                v-show="showingDetailsEmail"
                class="drop-options-alt-up left-mobile-m"
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

                  <button
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
                  </button>
                </header>

                <section v-if="allCompanyDetails.length">
                  <div
                    style="position: relative"
                    @click="rewritePitchWithDetails(detail.title, detail.details)"
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

                    <span @click="deleteCompanyDetails(detail.id)" class="absolute-icon">
                      <img src="@/assets/images/close.svg" height="10px" alt="" />
                    </span>
                  </div>
                </section>

                <section style="padding: 16px" v-else>
                  Your saved projects
                  <span>
                    <img
                      style="margin-right: 4px"
                      src="@/assets/images/folder.svg"
                      height="12px"
                      alt=""
                    />
                    will appear here.</span
                  >
                </section>
              </div>
            </div>
          </div>

          <div class="row">
            <!-- <button
              :disabled="
                loadingPitch || !subject || !targetEmail || sendingEmail || verifying || drafting
              "
              @click="createDraft"
              class="secondary-button"
            >
              <img
                v-if="drafting"
                style="margin-left: 4px"
                class="invert rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              {{ isMobile ? 'Save' : 'Save Draft' }}
            </button> -->

            <div v-if="sendingEmail" style="margin: 0 12px" class="loading-small">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
            <button
              v-else-if="hasGoogleIntegration || hasMicrosoftIntegration"
              @click="sendEmail"
              :disabled="
                loadingPitch || !subject || !targetEmail || sendingEmail || verifying || drafting
              "
              style="margin-right: 4px"
              class="primary-button"
              :class="{ opaque: loadingPitch || !subject || !targetEmail }"
            >
              <span> Send</span>
            </button>

            <button
              v-else-if="!hasGoogleIntegration && !hasMicrosoftIntegration"
              @click="goToIntegrations"
              style="margin-right: 4px"
              class="primary-button no-mar-mobile"
            >
              <span> {{ isMobile ? 'Connect' : ' Connect Email' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="googleModalOpen" class="bio-modal">
      <div class="bio-container">
        <header>
          <p style="padding: 8px 0; font-size: 22px" class="regen-header-title">
            {{ currentJournalist }}
          </p>

          <div style="margin-right: -2px" class="row">
            <div v-if="savingContact" style="margin: 0" class="loading-small">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>

            <!-- <button
              v-else
              @click="saveContact"
              class="s-wrapper img-container-button borderless clicked"
              :disabled="buttonClicked || loadingDraft || mainView === 'social'"
            >
              <img class="invert" src="@/assets/images/disk.svg" height="16px" alt="" />
              <div style="right: 120%" class="s-tooltip-below">Save to contacts</div>
            </button> -->
          </div>
        </header>

        <section v-if="loadingDraft">
          <div style="height: 40vh" class="bio-body">
            <div style="margin: 0" class="loading-small">
              <p style="margin-right: 8px">Generating bio for {{ currentJournalist }}</p>
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </section>

        <section class="mobile-body" v-else>
          <div class="bio-body" v-html="currentJournalistBio"></div>

          <aside>
            <img
              v-for="(url, i) in currentJournalistImages.slice(0, 5)"
              :key="i"
              :src="`${url}`"
              height="24px"
              alt=""
            />
          </aside>
        </section>

        <footer>
          <div class="row">
            <button
              class="secondary-button"
              :disabled="loadingDraft || savingContact"
              @click="toggleGoogleModal"
            >
              Close
            </button>
            <button
              class="primary-button"
              :disabled="loadingDraft || savingContact"
              @click="openDraftPitch"
            >
              Pitch Journalist
            </button>
          </div>
        </footer>
      </div>
    </Modal>

    <Modal v-if="inputModalOpen" class="paid-modal">
      <div
        :style="isMobile ? 'width: 95%; min-height: 275px' : 'width: 610px; min-height: 275px'"
        class="regen-container"
      >
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title">Learn Voice</h4>
            <p class="regen-header-subtitle">
              Provide a sample of the writing style you want to emulate
            </p>
          </div>
        </div>
        <div class="paid-body" style="overflow: hidden !important">
          <!-- <label for="styleName">Name</label> -->
          <input
            id="styleName"
            style="width: 100%; margin: 0.5rem 0 1rem 0"
            class="area-input-outline"
            placeholder="Style Name..."
            type="text"
            v-model="styleName"
            :disabled="savingStyle"
          />

          <!-- <label for="sample">Sample</label> -->
          <textarea
            id="sample"
            :disabled="savingStyle"
            maxlength="8000"
            class="area-input-outline wider"
            style="width: 100%; margin: 0.5rem 0 0 0; max-height: 280px"
            placeholder="Paste sample here..."
            v-model="sample"
            v-autoresize
          />
        </div>
        <footer class="paid-footer aligned-right">
          <button
            :disabled="savingStyle"
            @click="toggleLearnInputModal('')"
            class="secondary-button"
          >
            Cancel
          </button>
          <button
            :disabled="savingStyle || !styleName || !sample"
            @click="saveWritingStyle"
            class="primary-button"
          >
            {{ savingStyle ? 'Learning' : 'Learn' }}
            <div style="margin-left: 4px" v-if="savingStyle" class="loading-small">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </button>
        </footer>
      </div>
    </Modal>

    <Modal v-if="detailsInputModalOpen" class="paid-modal">
      <div
        :style="isMobile ? 'width: 95%; min-height: 275px' : 'width: 610px; min-height: 275px'"
        class="regen-container"
      >
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title">Add Project</h4>
            <p class="regen-header-subtitle">
              Provide project details (e.g. campaign, product launch, announcement, etc.)
            </p>
          </div>
        </div>
        <div class="paid-body" style="overflow: hidden !important">
          <!-- <label for="styleName">Name</label> -->
          <input
            id="styleName"
            style="width: 100%; margin: 0.5rem 0 1rem 0"
            class="area-input-outline"
            placeholder="Project name..."
            type="text"
            v-model="detailsName"
            :disabled="savingStyle"
          />

          <!-- <label for="sample">Sample</label> -->
          <textarea
            id="sample"
            :disabled="savingStyle"
            maxlength="800"
            class="area-input-outline wider"
            style="width: 100%; margin: 0.5rem 0 0 0; max-height: 280px"
            placeholder="Project details..."
            v-model="detailsBody"
            v-autoresize
          />
          <div class="flex-end">
            {{ detailsBody.length + '/800' }}
          </div>
        </div>
        <footer class="paid-footer aligned-right">
          <button :disabled="savingStyle" @click="toggleDetailsInputModal" class="secondary-button">
            Cancel
          </button>
          <button
            :disabled="savingStyle || !detailsName || !detailsBody"
            @click="addCompanyDetails"
            class="primary-button"
          >
            {{ savingStyle ? 'Adding' : 'Add' }}
            <div style="margin-left: 4px" v-if="savingStyle" class="loading-small">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </button>
        </footer>
      </div>
    </Modal>

    <Modal class="bio-modal med-modal" v-if="contactsModalOpen">
      <div class="bio-container med-container">
        <div class="header-alt">
          <h2 style="margin: 12px 0">Search Contact</h2>
          <p>Get a real-time bio along with pitching tips and contact details</p>
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
          <label for="outlet">Outlet</label>
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
              @click="getJournalistBioAlt"
              :disabled="loadingContacts || !outletName || !contactName"
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
            <button :disabled="savingContact" class="primary-button" @click="saveContactAlt">
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

    <Modal class="bio-modal med-modal" v-if="reportModalOpen">
      <div class="bio-container med-container">
        <div class="header-alt">
          <h2 style="margin: 12px 0">Generate Report</h2>
          <p>Generate a report based on this thread</p>
        </div>

        <div
          class="col"
          style="margin-top: 16px; margin-bottom: 24px; min-height: 120px; width: 100%"
        >
          <div class="col" style="margin-bottom: 8px">
            <label style="font-size: 16px" class="bold">Thread</label>
            <p>{{ savedSearch ? savedSearch.title : searchName }}</p>
          </div>

          <label style="font-size: 16px" class="bold" for="contact">Title</label>
          <input
            class="primary-input"
            type="text"
            name="contact"
            v-model="reportTitle"
            placeholder="Give your report a title..."
          />
          <label style="font-size: 16px" class="bold" for="outlet">Brand</label>
          <input
            class="primary-input"
            type="text"
            name="outlet"
            v-model="reportBrands"
            placeholder="Which brand is this report for (e.g. Nike, Tesla, FSU). Include multiple brands if applicable..."
          />
        </div>

        <footer>
          <div></div>
          <div class="row">
            <button class="secondary-button" @click="reportModalOpen = false">Cancel</button>
            <button
              @click="goToReports"
              :disabled="!reportBrands || !reportTitle"
              class="primary-button"
            >
              Continue
            </button>
          </div>
        </footer>
      </div>
    </Modal>

    <div style="margin-top: 16px; width: 100%" v-if="!selectedSearch">
      <div class="fadein" v-if="!chatting">
        <div class="small-container letter-spacing">
          <div>
            <div class="centered">
              <h1 style="color: #2f4656; font-size: 30px" class="bold-text">
                What would you like to search ?
              </h1>
            </div>
          </div>

          <div class="mobile-padding" style="width: 100%; padding: 0 10vw">
            <div class="large-input-container-alt">
              <div class="input-container-gray" :class="{ lbborder: newSearch }">
                <section>
                  <div style="margin: 8px 0 0 8px; width: 100%" class="row">
                    <!-- :placeholder="placeHolderText" -->
                    <!-- <div
                      @click="goToIntegrations"
                      v-if="mainView === 'social' && !hasTwitterIntegration"
                      class="abs-input-text"
                    >
                      <p>Connect X here</p>
                    </div> -->
                    <textarea
                      style="margin-left: -8px; width: 100%"
                      :rows="1"
                      id="search-input"
                      @keyup.enter="generateNewSearch($event, false)"
                      class="area-input"
                      autocomplete="off"
                      :placeholder="'Message ManagrAI...'"
                      v-model="newSearch"
                      v-autoresize
                      :disabled="loading || summaryLoading || isViewOnly"
                    />

                    <div
                      v-if="newSearch"
                      @click="generateNewSearch($event, false)"
                      class="left-margin pointer lite-bg img-container-stay"
                      style="margin-right: 24px"
                    >
                      <img
                        style="margin: 0"
                        src="@/assets/images/paper-plane-full.svg"
                        height="12px"
                        alt=""
                      />
                    </div>

                    <div
                      v-else
                      class="left-margin pointer img-container-stay"
                      style="margin-right: 24px; opacity: 0.4"
                    >
                      <img
                        style="margin: 0"
                        src="@/assets/images/paper-plane-full.svg"
                        height="12px"
                        alt=""
                      />
                    </div>
                  </div>

                  <div class="row">
                    <div style="margin: 12px 12px 0 18px" class="source-dropdown fadein">
                      <div @click.stop="toggleSources" class="drop-header img-blue s-wrapper">
                        <img
                          v-if="mainView === 'write'"
                          src="@/assets/images/edit.svg"
                          height="15px"
                          alt=""
                        />
                        <img
                          v-else-if="mainView === 'news'"
                          src="@/assets/images/globe.svg"
                          height="15px"
                          alt=""
                        />
                        <img
                          v-else-if="mainView === 'social'"
                          src="@/assets/images/thumb.svg"
                          height="15px"
                          alt=""
                        />
                        <img
                          v-else-if="mainView === 'web'"
                          src="@/assets/images/google.svg"
                          height="15px"
                          alt=""
                        />
                        <img
                          v-else-if="mainView === 'discover'"
                          src="@/assets/images/users.svg"
                          height="15px"
                          alt=""
                        />

                        <img
                          v-else-if="mainView === 'trending'"
                          src="@/assets/images/arrow-trend-up.svg"
                          height="11px"
                          alt=""
                        />

                        <img
                          v-else-if="mainView === 'omni'"
                          src="@/assets/images/brain.svg"
                          height="15px"
                          alt=""
                        />

                        <small>{{
                          mainView === 'discover' ? 'Media Contacts' : toCamelCase(mainView)
                        }}</small>
                        <!-- <img
                        v-if="!showingSources"
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
                      /> -->

                        <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Mode' }}</div>
                      </div>

                      <div
                        v-outside-click="hideSources"
                        v-show="showingSources"
                        class="drop-options-alt"
                      >
                        <header>
                          <h4>Mode</h4>

                          <p>Select the type of task you'd like ManagrAI to assist with</p>
                        </header>
                        <section>
                          <div
                            @click="switchMainView('omni')"
                            :class="{ activeswitch: mainView === 'discover' }"
                          >
                            <span>
                              <img src="@/assets/images/brain.svg" height="11px" alt="" />
                              Omni
                            </span>

                            <p>Search news, social and web</p>
                          </div>

                          <div
                            @click="switchMainView('news')"
                            :class="{ activeswitch: mainView === 'news' }"
                          >
                            <span>
                              <img src="@/assets/images/globe.svg" height="11px" alt="" />
                              News
                            </span>
                            <p>Search real-time news</p>
                          </div>

                          <div
                            @click="switchMainView('social')"
                            :class="{ activeswitch: mainView === 'social' }"
                          >
                            <span>
                              <img src="@/assets/images/thumb.svg" height="11px" alt="" />
                              Social
                            </span>

                            <p>Search top social posts</p>
                          </div>

                          <div
                            @click="switchMainView('web')"
                            :class="{ activeswitch: mainView === 'web' }"
                          >
                            <span>
                              <img src="@/assets/images/google.svg" height="11px" alt="" />
                              Web
                            </span>

                            <p>Search the web</p>
                          </div>

                          <!-- <div
                            @click="switchMainView('trending')"
                            :class="{ activeswitch: mainView === 'trending' }"
                          >
                            <span>
                              <img src="@/assets/images/arrow-trend-up.svg" height="11px" alt="" />
                              Trending
                            </span>

                            <p>Search trending news</p>
                          </div> -->

                          <div
                            @click="switchMainView('write')"
                            :class="{ activeswitch: mainView === 'write' }"
                          >
                            <span>
                              <img src="@/assets/images/edit.svg" height="11px" alt="" />
                              Write
                            </span>

                            <p>AI writing assistant</p>
                          </div>

                          <div
                            @click="toggleContactsModal"
                            :class="{ activeswitch: mainView === 'discover' }"
                          >
                            <span>
                              <img src="@/assets/images/users.svg" height="11px" alt="" />
                              Media Contacts
                            </span>

                            <p>Search media contacts</p>
                          </div>
                        </section>
                      </div>
                    </div>

                    <div
                      style="margin-right: 12px"
                      v-if="mainView === 'write'"
                      class="source-dropdown fadein"
                    >
                      <div
                        @click.stop="toggleShowStyles"
                        class="drop-header s-wrapper"
                        :class="{ 'soft-gray-bg': showingStyles }"
                      >
                        <img src="@/assets/images/wand.svg" height="15px" alt="" />

                        <small>{{ writingStyleTitle ? writingStyleTitle : 'Voice' }}</small>
                        <div class="s-tooltip">Voices</div>
                      </div>

                      <div
                        v-outside-click="hideStyles"
                        v-show="showingStyles"
                        class="drop-options-alt left-mobile"
                      >
                        <header>
                          <!-- <section class="h-padding">
                            <section @click="toggleStyles" class="toggle">
                              <span
                                :class="{ 'active-toggle': personalStyles }"
                                class="toggle-side"
                              >
                                <small>Personal</small>
                              </span>

                              <span
                                :class="{ 'active-toggle': !personalStyles }"
                                class="toggle-side"
                              >
                                <small>Group</small>
                              </span>
                            </section>
                          </section> -->

                          <h4>Voices</h4>
                          <p>Select a desired writing style or create your own</p>

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
                              {{ style.title }}
                            </span>
                            <p>{{ style.style }}</p>
                          </div>
                          <div
                            @mouseenter="setIndex(i)"
                            @mouseLeave="removeIndex"
                            @click="addWritingStyle(style.style, style.title)"
                            class="dropdown-item relative"
                            v-for="(style, i) in userWritingStyles"
                            :key="i"
                            :class="{ activeswitch: writingStyleTitle === style.title }"
                            :title="style.title"
                          >
                            <span>
                              {{ style.title }}
                            </span>
                            <p>{{ style.style }}</p>

                            <span
                              v-if="hoverIndex === i"
                              @click="deleteWritingStyle(style.id)"
                              class="absolute-icon"
                            >
                              <img src="@/assets/images/close.svg" height="12px" alt="" />
                            </span>
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

                        <footer class="space-between">
                          <span></span>
                          <button
                            @click="toggleLearnInputModal('')"
                            class="primary-button"
                            style="margin-right: 12px"
                          >
                            Create
                          </button>
                        </footer>
                      </div>
                    </div>

                    <div
                      @click="goToIntegrations"
                      style="margin-right: 12px; margin-top: 16px"
                      v-if="mainView === 'social' && !hasTwitterIntegration"
                      class="image-container s-wrapper"
                    >
                      <img src="@/assets/images/twitter-x.svg" height="14px" alt="" />
                      <div style="width: 120px" class="s-tooltip">Enable X searching</div>
                    </div>

                    <div
                      style="margin-right: 12px"
                      v-if="mainView !== 'discover'"
                      class="source-dropdown fadein"
                    >
                      <div
                        @click.stop="toggleMainDetails"
                        :class="{
                          'drop-header padding-right-x': detailTitle,
                          'soft-gray-bg': showingMainDetails,
                        }"
                        class="image-container s-wrapper"
                      >
                        <img src="@/assets/images/folder.svg" height="15px" alt="" />

                        <small v-if="detailTitle" :title="detailTitle">{{ detailTitle }}</small>
                        <div
                          class="image-container abs-right-img"
                          @click="clearDetails"
                          v-if="detailTitle"
                        >
                          <img src="@/assets/images/close.svg" height="12px" alt="" />
                        </div>
                        <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Projects' }}</div>
                      </div>

                      <div
                        v-outside-click="hideMainDetails"
                        v-if="showingMainDetails"
                        class="drop-options-alt"
                        :class="mainView === 'write' ? 'left-mobile-l' : 'left-mobile'"
                      >
                        <header>
                          <h4>Projects</h4>
                          <p>
                            Let ManagrAI know what you're working on (e.g. campaign, pitch, launch)
                          </p>
                          <!-- <button
                            @click="toggleDetailsInputModal"
                            class="secondary-button-no-border"
                            style="margin-right: 4px"
                          >
                            <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Details
                          </button> -->
                        </header>

                        <section v-if="allCompanyDetails.length && !editingProjects">
                          <div
                            style="position: relative"
                            @click="addDetails(detail.title, detail.details)"
                            v-for="detail in allCompanyDetails"
                            :key="detail.title"
                            :class="{ activesquareTile: detailTitle === detail.title }"
                            :title="detail.title"
                          >
                            <main v-if="!editingProjects">
                              <span style="max-width: 140px" class="ellipsis-text-s">
                                {{ detail.title }}
                              </span>
                              <p class="">{{ detail.details }}</p>

                              <span @click.stop="selectProject(detail)" class="absolute-icon">
                                <img src="@/assets/images/edit.svg" height="10px" alt="" />
                              </span>
                            </main>
                          </div>
                        </section>

                        <section v-else-if="editingProjects">
                          <textarea
                            v-model="selectedProject.details"
                            rows="3"
                            class="area-input text-area-input"
                            :class="{ opaquest: loadingPitch }"
                            v-autoresize
                            :placeholder="selectedProject.details"
                            style="
                              border: 1px solid rgba(0, 0, 0, 0.1) !important;
                              border-radius: 8px;
                              padding: 16px 8px;
                            "
                            maxlength="800"
                          ></textarea>
                        </section>

                        <section style="padding: 16px" v-else>
                          Your saved projects
                          <span>
                            <img
                              style="margin-right: 4px"
                              src="@/assets/images/folder.svg"
                              height="12px"
                              alt=""
                            />
                            will appear here.</span
                          >
                        </section>

                        <footer v-if="!editingProjects" class="space-between">
                          <span></span>
                          <button
                            :disabled="isViewOnly"
                            @click="toggleDetailsInputModal"
                            class="primary-button"
                            style="margin-right: 4px"
                          >
                            Add Project
                          </button>
                        </footer>

                        <footer v-else class="space-between">
                          <button
                            @click="deleteCompanyDetails(selectedProject.id)"
                            class="primary-button pinkbg"
                          >
                            Delete
                          </button>

                          <main class="row">
                            <button @click="editingProjects = false" class="secondary-button">
                              Cancel
                            </button>
                            <button @click="updateProject" class="primary-button">Update</button>
                          </main>
                        </footer>
                      </div>
                    </div>

                    <div
                      v-if="mainView === 'news' || mainView === 'social' || mainView === 'omni'"
                      class="row relative top-mar-mobile"
                    >
                      <div
                        @click.stop="toggleDate"
                        :class="{ 'soft-gray-bg': showDateSelection }"
                        class="image-container s-wrapper"
                      >
                        <img src="@/assets/images/calendar.svg" height="15px" alt="" />

                        <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Date' }}</div>
                      </div>

                      <div
                        v-outside-click="hideDate"
                        class="container-left-above left-mobile"
                        v-show="showDateSelection"
                        style="top: 40px"
                      >
                        <header>
                          <p>Date Range</p>
                        </header>

                        <div style="margin-top: 16px" class="row">
                          <input
                            class="area-input-smallest"
                            type="date"
                            :min="mainView === 'news' ? minDate : minDateSocial"
                            @input="validateDate"
                            v-model="dateStart"
                          />
                          <span style="margin: 0 12px"> - </span>

                          <input
                            class="area-input-smallest"
                            type="date"
                            :min="mainView === 'news' ? minDate : minDateSocial"
                            v-model="dateEnd"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>

            <div style="margin-top: 32px" class="centered">
              <div v-if="mainView === 'write'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in contentExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>
              <div v-else-if="mainView === 'news'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in newsExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>
              <div v-if="mainView === 'social'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in socialExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>
              <div v-if="mainView === 'discover'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in discoveryExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>
              <div v-if="mainView === 'web'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in webExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>
              <div v-if="mainView === 'trending'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in trendExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>

              <div v-else-if="mainView === 'omni'" style="gap: 12px" class="row">
                <div
                  @click="setNewSearch(example.value)"
                  v-for="example in omniExamples"
                  :key="example.value"
                  class="example-title"
                >
                  <img src="@/assets/images/lightbulb-on.svg" height="15px" alt="" />
                  {{ example.name }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="abs-bottom-right hide-mobile">
          <img
            @click.stop="toggleHelpMenu"
            src="@/assets/images/help.svg"
            class="pointer"
            height="26px"
            alt=""
          />
          <div v-outside-click="closeHelp" v-show="showingHelp" class="relative pointer">
            <div class="help-menu">
              <h4>Need Help ?</h4>
              <div v-if="!isPaid">
                <img src="@/assets/images/medal.svg" height="14px" alt="" />
                <a :href="upgradeLink" target="_blank">Upgrade to Pro</a>
              </div>
              <div style="background-color: white; cursor: text" v-else>
                <img
                  class="image-bg"
                  style="filter: none"
                  src="@/assets/images/smallLogo.png"
                  height="14px"
                  alt=""
                />
                <a style="text-decoration: none" class="pink-text">ManagrAI PRO</a>
              </div>
              <div>
                <img src="@/assets/images/camera.svg" height="14px" alt="" />
                <a :href="onboardingLink" target="_blank">Onboarding Video</a>
              </div>
              <div>
                <img src="@/assets/images/email-round.svg" height="14px" alt="" />
                <a :href="mailtoLink">Contact Support</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="search">
      <div style="height: 90vh" class="main center-content" v-if="loading || summaryLoading">
        <div style="padding: 16px 20vw; height: 100%; width: 100%" class="body">
          <div class="skeleton-loader">
            <div
              v-if="mainView !== 'omni'"
              style="margin-bottom: 24px"
              class="skeleton skeleton-title"
            ></div>

            <div class="row" v-else>
              <img
                style="filter: invert(40%); margin-right: 10px"
                src="@/assets/images/brain.svg"
                height="20px"
                alt=""
              />
              <p style="font-size: 20px" class="bold-text">Omni Search</p>
            </div>

            <div
              v-if="!articlesFiltered.length && mainView !== 'omni'"
              style="justify-content: space-between"
              class="row"
            >
              <div class="skeleton skeleton-img"></div>
              <div class="skeleton skeleton-img"></div>
              <div class="skeleton skeleton-img"></div>
              <div class="skeleton skeleton-img"></div>
            </div>

            <div
              style="width: 100%; justify-content: space-between"
              class="row fadein"
              v-else-if="
                (mainView === 'news' || mainView === 'trending') && articlesFiltered.length
              "
            >
              <div style="width: 24%" v-for="(article, i) in articlesFiltered.slice(0, 4)" :key="i">
                <img
                  :src="article.image_url ? article.image_url : article.image"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div>

            <div style="margin-left: 3px" v-if="mainView === 'omni'">
              <div :class="{ opaquer: searchingType !== 'news' }" class="omni-load">
                <div :class="{ pulse: searchingType === 'news' }" class="row">
                  <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                  <p class="bold-text">Searching thousands of news outlets</p>
                </div>

                <p
                  class="bold-text fadein"
                  style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                  v-if="searchingType === 'news'"
                >
                  Reading ...
                </p>

                <div style="margin-left: 24px" class="fadein row" v-if="omniNews.length">
                  <button
                    style="margin-right: 8px"
                    class="secondary-button fadein"
                    v-for="(article, i) in omniNews.slice(0, 4)"
                    :key="i"
                  >
                    <img
                      :src="article.image_url ? article.image_url : logoPlaceholder"
                      height="12px"
                      alt=""
                      style="margin: 0 8px 0 1px"
                    />

                    {{ article.source.name }}
                  </button>
                </div>
              </div>

              <div :class="{ opaquer: searchingType !== 'social' }" class="omni-load">
                <div :class="{ pulse: searchingType === 'social' }" class="row">
                  <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                  <p class="bold-text">Sifting through top social media posts</p>
                </div>

                <p
                  class="bold-text fadein"
                  style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                  v-if="searchingType === 'social'"
                >
                  Reading ...
                </p>

                <div style="margin-left: 24px" class="fadein row" v-if="omniSocial.length">
                  <button
                    style="margin-right: 8px"
                    class="secondary-button fadein"
                    v-for="(article, i) in omniSocial.slice(0, 4)"
                    :key="i"
                  >
                    <img
                      v-if="article.type === 'youtube'"
                      :src="youtubePlaceholder"
                      height="12px"
                      alt=""
                      style="margin: 0 8px 0 1px"
                    />
                    <img
                      v-else-if="article.type === 'bluesky'"
                      :src="blueskyPlaceholder"
                      height="14px"
                      alt=""
                      style="margin: 0 8px 0 1px"
                    />
                    <img
                      v-else-if="article.type === 'twitter'"
                      :src="twitterPlaceholder"
                      height="12px"
                      alt=""
                      style="margin: 0 8px 0 1px"
                    />

                    <div v-if="article.type === 'twitter'">{{ article.user.username }}</div>
                    <div v-else>{{ article.author }}</div>
                  </button>
                </div>
              </div>

              <div :class="{ opaquer: searchingType !== 'web' }" class="omni-load">
                <div :class="{ pulse: searchingType === 'web' }" class="row">
                  <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                  <p class="bold-text">Scouring the web</p>
                </div>

                <p
                  class="bold-text fadein"
                  style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                  v-if="searchingType === 'web'"
                >
                  Reading ...
                </p>

                <div style="margin-left: 24px" class="fadein row" v-if="omniWeb.length">
                  <button
                    style="margin-right: 8px"
                    class="secondary-button fadein"
                    v-for="(article, i) in omniWeb.slice(0, 4)"
                    :key="i"
                  >
                    <img
                      :src="
                        article.source && article.source_img ? article.source_img : globePlaceholder
                      "
                      height="12px"
                      alt=""
                      style="margin: 0 8px 0 1px"
                    />
                    <small>{{ article.source }}</small>
                  </button>
                </div>
              </div>

              <div :class="{ opaquer: searchingType !== 'summary' }" class="omni-load">
                <div :class="{ pulse: searchingType === 'summary' }" class="row">
                  <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                  <p class="bold-text">Generating summary</p>
                </div>

                <!-- <p
                  class="bold-text fadein"
                  style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                  v-if="searchingType === 'summary'"
                >
                  Summarizing ...
                </p> -->

                <div style="padding: 8px 0 0 0; margin-left: 24px" class="skeleton-loader fadein">
                  <div
                    v-if="searchingType === 'summary'"
                    style="margin-bottom: 16px"
                    class="skeleton skeleton-title"
                  ></div>

                  <div v-if="searchingType === 'summary'" class="skeleton skeleton-text"></div>
                  <div v-if="searchingType === 'summary'" class="skeleton skeleton-text"></div>
                </div>
              </div>
            </div>

            <!-- <div
              style="width: 100%; justify-content: space-between; margin-top: 32px"
              class="row fadein"
              v-if="mainView === 'omni' && omniNews.length"
            >
              <div style="width: 24%" v-for="(article, i) in omniNews.slice(0, 4)" :key="i">
                <img
                  :src="article.image_url ? article.image_url : logoPlaceholder"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div> -->

            <div
              v-if="mainView !== 'omni'"
              style="margin-top: 24px"
              class="skeleton skeleton-text"
            ></div>
            <div v-if="mainView !== 'omni'" class="skeleton skeleton-text"></div>
            <div v-if="mainView !== 'omni'" class="skeleton skeleton-large"></div>
            <div v-if="mainView !== 'omni'" class="skeleton skeleton-text"></div>
            <div v-if="mainView !== 'omni'" class="skeleton skeleton-text"></div>
            <div
              v-if="mainView !== 'omni'"
              style="margin-top: 12px"
              class="skeleton skeleton-title"
            ></div>
            <div v-if="mainView !== 'omni'" class="skeleton skeleton-text"></div>
          </div>
        </div>

        <!-- <aside style="margin-top: -40px">
          <div class="section">
            <div class="skeleton-loader">
              <div class="skeleton skeleton-large"></div>
            </div>
          </div>
        </aside> -->
      </div>

      <section v-else class="center-content main fadein">
        <div
          ref="loadedContent"
          style="position: relative"
          :class="['widebody', { contentShiftAlt: showingArticles }]"
        >
          <header class="content-header-test">
            <div class="row-top">
              <div
                v-if="!isViewOnly"
                style="margin-top: 16px"
                class="image-container xxl-margin"
                @click="resetAll"
              >
                <img src="@/assets/images/goBack.svg" height="17px" alt="" />
              </div>

              <p
                v-if="
                  mainView === 'news' && !(filteredArticles && filteredArticles.length) && !summary
                "
                class="sub-text ellipsis-text-test"
                style="margin: 18px 0 0 0"
              >
                No results found. Try a new search...
              </p>

              <p
                v-else-if="mainView === 'social' && !tweets.length && !summary"
                class="sub-text ellipsis-text-test"
                style="margin: 18px 0 0 0"
              >
                No results found. Try a new search...
              </p>

              <p
                v-else-if="mainView === 'web' && !googleResults.length && !summary"
                class="sub-text ellipsis-text-test"
                style="margin: 18px 0 0 0"
              >
                No results found. Try a new search...
              </p>

              <!-- <p
                v-else-if="mainView === 'news'"
                class="sub-text ellipsis-text-test"
                style="margin: 16px 0"
              >
                <span :title="originalSearch">{{ originalSearch }}</span>
              </p> -->

              <p v-else class="sub-text ellipsis-text-bold" style="margin: 16px 0">
                <span :title="newSearch">{{ newSearch }}</span>
              </p>
            </div>

            <div style="padding-top: 16px" v-if="summary" class="row">
              <!-- <div
                @click="toggleLearnInputModal(summary)"
                v-if="mainView === 'write'"
                class="image-container s-wrapper"
              >
                <img
                  style="cursor: pointer; filter: invert(40%)"
                  src="@/assets/images/wand.svg"
                  height="16px"
                  alt=""
                />

                <div class="s-tooltip">Learn this style</div>
              </div> -->

              <!-- <div
                @click.stop="toggleCompany"
                :class="{ 'soft-gray-bg': showCompanySelection || detailTitle }"
                class="image-container s-wrapper"
              >
             
                <img src="@/assets/images/building.svg" height="14px" alt="" />
                <div
                  style="bottom: 115%; width: 200px; left: -40px"
                  v-if="mainView !== 'discover'"
                  class="s-tooltip"
                >
                  Company Details: for pitching
                </div>
                <div style="bottom: 115%; width: 200px; left: -40px" v-else class="s-tooltip">
                  Company Details: for pitching tips
                </div>
              </div> -->
              <div
                v-if="mainView !== 'omni'"
                @click.stop="openReportModal"
                :class="{ 'soft-gray-bg': showDateSelection }"
                class="img-container-button s-wrapper"
                style="
                  margin-right: 8px;
                  border: 1px solid rgba(0, 0, 0, 0.2);
                  padding: 6px 7px 3px 7px;
                "
              >
                <img class="invert" src="@/assets/images/chart.svg" height="13px" alt="" />

                <div
                  :class="{ widetip: (!searchSaved && !isViewOnly) || reportCredits < 1 }"
                  class="s-tooltip"
                >
                  {{
                    isViewOnly
                      ? 'Locked'
                      : reportCredits < 1
                      ? 'Upgrade to PRO'
                      : searchSaved
                      ? 'Generate Report'
                      : 'Save Thread to enable report'
                  }}
                </div>
              </div>

              <button
                v-if="!isViewOnly"
                @click.stop="showShare"
                class="img-container-button s-wrapper"
                :class="{ 'soft-gray-bg': showingShare }"
                :disabled="!searchSaved"
                style="border: 1px solid rgba(0, 0, 0, 0.2) !important; padding: 6px 7px 3px 7px"
              >
                <img class="invert" src="@/assets/images/share.svg" height="13px" alt="" />
                <div v-if="!searchSaved && !isViewOnly" style="width: 150px" class="s-tooltip">
                  Save to enable sharing
                </div>
                <div v-else-if="isViewOnly" class="s-tooltip">Locked</div>
                <div v-else class="s-tooltip">Share thread</div>
              </button>

              <!-- <div @click="copyText" v-if="mainView === 'write'" class="secondary-button">
                <div>{{ copyTip }}</div>
              </div> -->

              <!-- <div
                @click="copyDiscoverText"
                v-else-if="mainView === 'discover'"
                class="secondary-button"
              >
               

                <div>{{ copyTip }}</div>
              </div> -->

              <button
                class="primary-button"
                :class="{
                  'soft-gray-bg blk-text':
                    mainView !== 'news' &&
                    mainView !== 'social' &&
                    (savedDiscovery || savedPitch) &&
                    !notifiedList.includes(searchId) &&
                    !notifiedList.includes(threadId),
                }"
                @click.stop="showSave"
                v-if="
                  (filteredArticles && filteredArticles.length) ||
                  tweets.length ||
                  (mainView === 'write' && summary) ||
                  (mainView === 'discover' && summary) ||
                  (mainView === 'web' && summary) ||
                  (mainView === 'omni' && summary && !isViewOnly)
                "
                :disabled="searchSaved && mainView !== 'news' && mainView !== 'social'"
              >
                <!-- <img
                  v-if="
                    (mainView === 'news' || mainView === 'social') &&
                    (searchSaved || savedSearch) &&
                    !notifiedList.includes(searchId)
                  "
                  src="@/assets/images/bell.svg"
                  height="14p"
                  alt=""
                />

                <img
                  v-else-if="
                    (mainView === 'news' || mainView === 'social') &&
                    (searchSaved || savedSearch) &&
                    notifiedList.includes(searchId)
                  "
                  src="@/assets/images/bell-slash.svg"
                  height="14p"
                  alt=""
                />

                <img
                  v-else-if="
                    mainView !== 'news' &&
                    mainView !== 'social' &&
                    (savedDiscovery || savedPitch) &&
                    !notifiedList.includes(searchId)
                  "
                  height="14px"
                  src="@/assets/images/disk.svg"
                  style="opacity: 0.4"
                  alt=""
                />

                <img v-else height="14px" src="@/assets/images/disk.svg" alt="" /> -->

                <div
                  v-if="
                    (mainView === 'news' || mainView === 'social') &&
                    (searchSaved || savedSearch) &&
                    !notifiedList.includes(searchId) &&
                    !notifiedList.includes(threadId)
                  "
                >
                  Schedule Digest
                </div>

                <div
                  v-else-if="
                    (mainView === 'news' || mainView === 'social') &&
                    (searchSaved || savedSearch) &&
                    (notifiedList.includes(searchId) || notifiedList.includes(threadId))
                  "
                >
                  Disable Digest
                </div>

                <div v-else>Save</div>
              </button>

              <div
                v-outside-click="hideCompany"
                v-show="showCompanySelection && mainView !== 'web'"
                class="source-dropdown"
                style="margin: 0; bottom: 16px"
              >
                <div class="drop-options-alternate">
                  <header style="padding-top: 8px; padding-bottom: 8px" class="space-between">
                    <button
                      @click="toggleDetailsInputModal"
                      class="secondary-button-no-border"
                      style="margin-right: 4px"
                    >
                      <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Details
                    </button>

                    <button
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
                    </button>
                  </header>

                  <section v-if="allCompanyDetails.length">
                    <div
                      style="position: relative"
                      @click="addDetailsAlt(detail.title, detail.details)"
                      v-for="detail in allCompanyDetails"
                      :key="detail.title"
                      :class="{ activesquareTile: detailTitle === detail.title }"
                      :title="detail.title"
                    >
                      <span class="">
                        {{ detail.title }}
                      </span>
                      <p class="">{{ detail.details }}</p>

                      <span @click="deleteCompanyDetails(detail.id)" class="absolute-icon">
                        <img src="@/assets/images/close.svg" height="10px" alt="" />
                      </span>
                    </div>
                  </section>

                  <section style="padding: 16px" v-else>
                    Your saved projects
                    <span>
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/folder.svg"
                        height="12px"
                        alt=""
                      />
                      will appear here.</span
                    >
                  </section>
                </div>
              </div>

              <div class="dropdown-small" v-outside-click="hideShare" v-show="showingShare">
                <div style="padding-bottom: 12px" class="dropdown-small-header dropdown-small-bb">
                  <p style="margin: 0">Share Thread</p>
                  <small style="color: #555f71">Below is a shareable link to this thread</small>
                </div>
                <div class="dropdown-small-section">
                  <div v-if="savedSearch" class="row">
                    <img
                      style="margin-right: 8px"
                      src="@/assets/images/link.svg"
                      height="12px"
                      alt=""
                    />
                    <a
                      :href="savedSearch.share_url"
                      target="_blank"
                      style="max-width: 250px; margin: 0"
                      class="ellipsis-text-s share-link"
                    >
                      {{ savedSearch.share_url }}
                    </a>
                  </div>

                  <div v-else class="row">
                    <img
                      style="margin-right: 8px"
                      src="@/assets/images/link.svg"
                      height="12px"
                      alt=""
                    />
                    <small style="max-width: 250px; margin: 0" class="ellipsis-text-s share-link">
                      link not generated
                    </small>
                  </div>
                  <!-- <label for="shareEmail">Email</label>
                  <input
                    class="area-input-outline"
                    name="shareEmail"
                    v-model="shareEmail"
                    type="text"
                    style="width: 100%"
                  />
                  <div>
                    <button
                      @click="sendSummaryEmail"
                      :disabled="!shareEmail"
                      class="primary-button"
                    >
                      <img
                        v-if="sendingSummaryEmail"
                        class="rotation innvert"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      <img v-else src="@/assets/images/email-round.svg" height="14px" alt="" /> Send
                      Email
                    </button>
                  </div> -->
                </div>
                <!-- <div class="dropdown-small-section">
                  <label for="slackChannel">Slack</label>

                  <div>
                    <div class="dropdown-select">
                      <div @click.stop="showChannels" class="dropdown-select-header">
                        {{ channelId ? channelName : 'Select a Slack channel' }}
                        <img src="@/assets/images/downArrow.svg" height="14px" alt="" />
                      </div>

                      <div
                        v-outside-click="hideChannels"
                        v-show="showingChannels"
                        class="dropdown-select-body"
                      >
                        <div class="dropdown-select-top">
                          <div style="width: 100% !important" class="input">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                              <path
                                fill-rule="evenodd"
                                clip-rule="evenodd"
                                d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                                fill="currentColor"
                              ></path>
                            </svg>
                            <input
                              v-model="searchChannelText"
                              class="search-input"
                              :placeholder="`Search...`"
                            />

                            <img
                              v-if="searchChannelText"
                              @click="clearSearchText"
                              src="@/assets/images/close.svg"
                              class="pointer"
                              height="12px"
                              alt=""
                            />
                          </div>
                        </div>

                        <div v-show="filteredChannels.length" style="min-height: 180px">
                          <div
                            v-for="(channel, i) in filteredChannels"
                            :key="i"
                            class="dropdown-select-item"
                            @click="selectChannel(channel)"
                          >
                            {{ channel.name }}
                          </div>
                        </div>

                        <div style="height: 180px" v-show="!filteredChannels.length">
                          <p style="margin-left: 12px">No results...</p>
                        </div>

                        <div class="dropdown-select-bottom">
                          <button
                            style="position: sticky; bottom: 0"
                            class="secondary-button"
                            @click="listUserChannels(userChannelOpts.nextCursor)"
                            :disabled="dropdownLoading || !userChannelOpts.nextCursor"
                          >
                            <img
                              v-if="dropdownLoading"
                              class="rotation innvert"
                              src="@/assets/images/loading.svg"
                              height="14px"
                              alt=""
                            />
                            Load more
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <button
                      v-if="user.slackRef"
                      :disabled="!user.slackRef || !channelId"
                      @click="sendToSlack"
                      class="secondary-button"
                    >
                      <img
                        v-if="sendingSlack"
                        class="rotation innvert"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      <img v-else src="@/assets/images/slackLogo.png" height="14px" alt="" /> Send
                      to Slack
                    </button>

                    <button v-else @click="goToIntegrations" class="secondary-button">
                      <img src="@/assets/images/slackLogo.png" height="14px" alt="" />
                      Connect Slack
                    </button>
                  </div>
                </div> -->

                <div class="flex-end">
                  <div style="width: fit-content; padding-bottom: 12px" class="row">
                    <button @click="hideShare" style="margin: 0 8px" class="secondary-button">
                      Close
                    </button>
                    <button style="margin: 0" @click="copyShareThread" class="primary-button">
                      {{ copyShareTip }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="dropdown-small" v-outside-click="hideSave" v-show="showingSave">
                <div v-if="mainView === 'write' && !savedPitch" class="dropdown-small-header">
                  Save this content
                </div>
                <div v-else-if="mainView === 'write'" class="dropdown-small-header opaquest">
                  Save this content
                </div>

                <div
                  v-else-if="mainView === 'discover' && !savedDiscovery"
                  class="dropdown-small-header"
                >
                  Save this list
                </div>
                <div v-else-if="mainView === 'discover'" class="dropdown-small-header opaquest">
                  Save this list
                </div>

                <div
                  v-else-if="
                    (mainView === 'news' || mainView === 'social') && (searchSaved || savedSearch)
                  "
                  class="dropdown-small-header opaquest"
                >
                  Save Thread
                </div>
                <div v-else class="dropdown-small-header">Save Thread</div>

                <!-- <div v-if="mainView === 'write'" class="dropdown-small-section">
                  <label
                    :class="{ opaquest: savedPitch }"
                    style="font-size: 13px"
                    for="detail-title"
                    >Name</label
                  >
                  <input
                    id="detail-title"
                    style="width: 100%"
                    class="area-input-outline"
                    type="text"
                    placeholder="Name your content..."
                    v-model="pitchName"
                    :disabled="savedPitch"
                  />

                  <div>
                    <button
                      @click="savePitch"
                      class="primary-button"
                      :disabled="
                        articleSummaryLoading || loading || savingSearch || savedPitch || !pitchName
                      "
                    >
                      <img
                        v-if="savingSearch"
                        class="rotation innvert"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      Save
                    </button>
                  </div>
                </div> -->

                <!-- <div v-else-if="mainView === 'discover'" class="dropdown-small-section">
                  <label
                    :class="{ opaquest: savedDiscovery }"
                    style="font-size: 13px"
                    for="detail-title"
                    >Name</label
                  >
                  <input
                    id="detail-title"
                    style="width: 100%"
                    class="area-input-outline"
                    type="text"
                    placeholder="Name your list..."
                    v-model="listName"
                    :disabled="savedDiscovery"
                  />

                  <div>
                    <button
                      @click="saveDiscovery"
                      class="primary-button"
                      :disabled="
                        articleSummaryLoading ||
                        loading ||
                        summaryLoading ||
                        savingSearch ||
                        savedDiscovery ||
                        !listName
                      "
                    >
                      <img
                        v-if="savingSearch"
                        class="rotation innvert"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      Save
                    </button>
                  </div>
                </div> -->

                <div class="dropdown-small-section dropdown-small-bb">
                  <label
                    :class="{ opaquest: searchSaved || savedSearch }"
                    style="font-size: 13px"
                    for="detail-title"
                    >Name</label
                  >
                  <input
                    id="detail-title"
                    style="width: 100%"
                    class="area-input-outline"
                    type="text"
                    placeholder="Thread name..."
                    v-model="searchName"
                    :disabled="searchSaved"
                  />

                  <div>
                    <button
                      @click="saveThread"
                      class="primary-button"
                      :disabled="
                        articleSummaryLoading ||
                        loading ||
                        summaryLoading ||
                        savingSearch ||
                        !searchName ||
                        searchSaved
                      "
                    >
                      <img
                        v-if="savingSearch"
                        class="rotation innvert"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      Save
                    </button>
                  </div>
                </div>

                <div
                  v-if="
                    (mainView === 'news' || mainView === 'social') &&
                    !notifiedList.includes(searchId) &&
                    !notifiedList.includes(threadId)
                  "
                  class="dropdown-small-section"
                >
                  <label v-if="savedSearch || savedDiscovery || savedPitch" for="time-select"
                    >Schedule Daily Digest</label
                  >
                  <label class="opaquest" v-else for="time-select">Schedule Daily Digest</label>

                  <input
                    id="time-select"
                    style="width: 100%"
                    class="area-input-outline"
                    required
                    @input="calculateDate(alertTIme)"
                    type="time"
                    v-model="alertTIme"
                    :disabled="
                      savingAlert || !isPaid || (!savedSearch && !savedDiscovery && !savedPitch)
                    "
                  />

                  <!-- <div style="margin: 8px 0" class="space-between">
                    <div class="row">
                      <img
                        src="@/assets/images/email-round.svg"
                        height="14px"
                        alt=""
                        style="margin-right: 8px; opacity: 0.7"
                      />
                      Send digest to email
                    </div>

                    <label class="switch">
                      <input
                        :checked="alertType === 'EMAIL'"
                        @change="toggleAlert('EMAIL')"
                        type="checkbox"
                      />
                      <span class="slider round"></span>
                    </label>
                  </div> -->

                  <!-- <div
                    v-if="user.slackRef && mainView === 'news'"
                    style="margin-bottom: 16px"
                    class="space-between"
                  >
                    <div class="row">
                      <img
                        src="@/assets/images/slackLogo.png"
                        height="14px"
                        alt=""
                        style="margin-right: 8px"
                      />
                      Send digest to Slack
                    </div>

                    <label class="switch">
                      <input
                        :checked="alertType === 'SLACK'"
                        @change="toggleAlert('SLACK')"
                        type="checkbox"
                      />
                      <span class="slider round"></span>
                    </label>
                  </div>

                  <div
                    v-else-if="mainView === 'news'"
                    style="margin-bottom: 16px"
                    class="space-between"
                  >
                    <div class="row">
                      <img
                        src="@/assets/images/slackLogo.png"
                        height="14px"
                        alt=""
                        style="margin-right: 8px"
                      />
                      Send digest to Slack
                    </div>

                    <button @click="goToIntegrations" class="secondary-button">
                      <img src="@/assets/images/slackLogo.png" height="14px" alt="" />
                      Connect
                    </button>
                  </div> -->

                  <!-- <div style="width: 100%" class="fadein" v-show="alertType === 'SLACK'">
                    <div class="dropdown-select">
                      <div @click.stop="showAlertChannels" class="dropdown-select-header">
                        {{ alertChannel ? alertChannelName : 'Select a Slack channel' }}
                        <img src="@/assets/images/downArrow.svg" height="14px" alt="" />
                      </div>

                      <div
                        v-outside-click="hideAlertChannels"
                        v-show="showingAlertChannels"
                        class="dropdown-select-body-up"
                      >
                        <div class="dropdown-select-top">
                          <div style="width: 100% !important" class="input">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                              <path
                                fill-rule="evenodd"
                                clip-rule="evenodd"
                                d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                                fill="currentColor"
                              ></path>
                            </svg>
                            <input
                              v-model="searchChannelText"
                              class="search-input"
                              :placeholder="`Search...`"
                            />

                            <img
                              v-if="searchChannelText"
                              @click="clearSearchText"
                              src="@/assets/images/close.svg"
                              class="pointer"
                              height="12px"
                              alt=""
                            />
                          </div>
                        </div>

                        <div v-show="filteredChannels.length" style="min-height: 180px">
                          <div
                            v-for="(channel, i) in filteredChannels"
                            :key="i"
                            class="dropdown-select-item"
                            @click="selectAlertChannel(channel)"
                          >
                            {{ channel.name }}
                          </div>
                        </div>

                        <div style="height: 180px" v-show="!filteredChannels.length">
                          <p style="margin-left: 12px">No results...</p>
                        </div>

                        <div class="dropdown-select-bottom">
                          <button
                            style="position: sticky; bottom: 0"
                            class="secondary-button"
                            @click="listUserChannels(userChannelOpts.nextCursor)"
                            :disabled="dropdownLoading || !userChannelOpts.nextCursor"
                          >
                            <img
                              v-if="dropdownLoading"
                              class="rotation innvert"
                              src="@/assets/images/loading.svg"
                              height="14px"
                              alt=""
                            />
                            Load more
                          </button>
                        </div>
                      </div>
                    </div>
                  </div> -->

                  <div class="row-end-bottom" style="margin-top: 0">
                    <button @click="hideSave" class="secondary-button">Close</button>

                    <button
                      @click="addEmailAlert"
                      :disabled="
                        savingAlert ||
                        !alertTIme ||
                        !isPaid ||
                        (!savedSearch && !savedDiscovery && !savedPitch) ||
                        !alertType ||
                        (alertType === 'SLACK' && !alertChannel)
                      "
                      style="margin-left: 8px"
                      class="primary-button"
                      v-if="!alertSet && !showingAlertChannels"
                    >
                      Schedule
                    </button>
                  </div>
                </div>

                <div
                  class="dropdown-small-section"
                  v-if="
                    (mainView === 'news' || mainView === 'social') &&
                    (searchSaved || savedSearch) &&
                    (notifiedList.includes(searchId) || notifiedList.includes(threadId))
                  "
                >
                  <label>Disable Digest</label>
                  <input
                    style="width: 100%"
                    class="area-input-outline"
                    disabled
                    type="text"
                    :placeholder="searchTime"
                  />

                  <div class="row-end-bottom" style="margin-top: 0">
                    <!-- <button class="primary-button" @click="testEmailAlert">Send Preview</button> -->
                    <button @click="hideSave" class="secondary-button">Close</button>
                    <button
                      style="margin-left: 8px"
                      class="primary-button"
                      @click="removeEmailAlert"
                    >
                      Disable Digest
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </header>
          <section class="content-container">
            <div
              style="width: 100%; justify-content: space-between"
              class="row"
              v-if="mainView === 'news' || mainView === 'trending'"
            >
              <div style="width: 24%" v-for="(article, i) in articlesFiltered.slice(0, 4)" :key="i">
                <img
                  @click="setOriginalArticles"
                  :src="article.image ? article.image : article.image_url"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div>

            <div
              style="width: 100%; justify-content: space-between"
              class="row"
              v-else-if="mainView === 'omni' && omniNews.length"
            >
              <div style="width: 24%" v-for="(article, i) in omniNews.slice(0, 4)" :key="i">
                <img
                  @click="setOriginalArticles"
                  :src="article.image_url ? article.image_url : logoPlaceholder"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div>

            <div
              style="width: 100%; justify-content: space-between"
              class="row"
              v-else-if="mainView === 'omni' && !omniNews.length"
            >
              <div style="width: 24%" v-for="(article, i) in omniSocial.slice(0, 4)" :key="i">
                <img
                  v-if="article.type === 'twitter'"
                  @click="setOriginalArticles"
                  :src="
                    article.user.profile_image_url
                      ? article.user.profile_image_url
                      : twitterPlaceholder
                  "
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />

                <img
                  v-else-if="article.type === 'youtube'"
                  @click="setOriginalArticles"
                  :src="article.image_url ? article.image_url : youtubePlaceholder"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />

                <img
                  v-else
                  @click="setOriginalArticles"
                  :src="article.image_url ? article.image_url : blueskyPlaceholder"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div>

            <div
              style="width: 100%; justify-content: space-between"
              class="row"
              v-else-if="mainView === 'web'"
            >
              <div style="width: 24%" v-for="(result, i) in filteredResults.slice(0, 4)" :key="i">
                <img
                  @click="setOriginalArticles"
                  :src="result.image"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div>

            <div
              style="width: 100%; justify-content: space-between"
              class="row"
              v-else-if="mainView === 'social'"
            >
              <div class="row" style="width: 100%; gap: 8px" v-if="tweetMedia && tweetMedia.length">
                <div
                  style="width: 24%"
                  v-for="media in tweetMedia.slice(0, 4)"
                  :key="media.media_key"
                >
                  <div>
                    <img
                      @click="setOriginalArticles"
                      v-if="media.type === 'photo'"
                      :src="media.url"
                      class="card-photo-header-small"
                      alt=""
                    />

                    <video
                      @click="setOriginalArticles"
                      v-else-if="media.type === 'video'"
                      class="card-photo-header-small"
                      controls
                    >
                      <source :src="media.variants[1].url" type="video/mp4" />
                    </video>

                    <video
                      @click="setOriginalArticles"
                      v-else-if="media.type === 'animated_gif'"
                      class="card-photo-header-small"
                      autoplay
                      loop
                      muted
                      playsinline
                    >
                      <source :src="media.variants[0].url" type="video/mp4" />
                    </video>
                  </div>
                </div>
              </div>

              <div
                v-else
                style="width: 24%"
                v-for="(tweet, i) in filteredTweets.slice(0, 4)"
                :key="i"
              >
                <img
                  @click="setOriginalArticles"
                  :src="tweet.image_url ? tweet.image_url : blueskyPlaceholder"
                  @error="onImageError($event)"
                  class="card-photo-header-small"
                />
              </div>
            </div>

            <div
              v-if="
                (!(filteredArticles && filteredArticles.length) && !summary) ||
                (!(filteredTweets && filteredTweets.length) && !summary)
              "
            >
              <div class="citation-text" v-html="noResultsString"></div>
              <!-- <div
                style="margin: 12px 0"
                class="row"
                v-if="mainView === 'news' || mainView === 'social'"
              >
                <div
                  @click="toggleType(mainView === 'news' ? 'social' : 'news')"
                  class="s-wrapper"
                  style="margin-right: 12px; cursor: pointer"
                >
                  <img
                    v-if="mainView === 'news'"
                    src="@/assets/images/thumb.svg"
                    height="16px"
                    alt=""
                  />
                  <img
                    v-else-if="mainView === 'social'"
                    src="@/assets/images/globe.svg"
                    height="16px"
                    alt=""
                  />
                  <div class="s-tooltip">
                    {{
                      isViewOnly
                        ? 'Locked'
                        : mainView === 'news'
                        ? 'Switch to Social'
                        : 'Switch to News'
                    }}
                  </div>
                </div>

                <div @click="toggleType('web')" style="cursor: pointer" class="s-wrapper">
                  <img src="@/assets/images/google.svg" height="16px" alt="" />
                  <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Switch to Web' }}</div>
                </div>
              </div> -->
            </div>

            <div v-else class="content-padding relative">
              <div
                style="width: 100%"
                v-if="summary"
                class="space-between abs-container"
                :class="{ lessTop: mainView === 'write' }"
              >
                <!-- <img
                style="margin-right: 8px"
                src="@/assets/images/sparkle.svg"
                height="14px"
                alt=""
              />

              <p class="header-p">Answer</p> -->
                <div></div>

                <div
                  v-if="mainView !== 'discover'"
                  style="margin: 2px 0 0 4px"
                  class="image-container s-wrapper"
                >
                  <img
                    style="cursor: pointer; filter: invert(40%)"
                    src="@/assets/images/clipboard.svg"
                    height="16px"
                    alt=""
                    @click="copyText"
                  />

                  <div class="s-tooltip">{{ copyTip }}</div>
                </div>
              </div>
              <div
                style="margin-top: 32px"
                v-if="mainView === 'social'"
                v-html="insertTweetCitations(summary)"
                class="citation-text"
              ></div>
              <div
                style="margin-top: 32px"
                v-else-if="mainView === 'news' || mainView === 'trending'"
                v-html="insertNewsCitations(summary)"
                class="citation-text"
              ></div>
              <div
                style="margin-top: 16px"
                v-else-if="mainView === 'web'"
                class="citation-text"
                v-html="insertCitations(summary)"
              ></div>
              <div
                style="margin-top: 32px"
                v-else-if="mainView === 'omni'"
                v-html="insertOmniCitations(summary)"
                class="citation-text"
              ></div>
              <div
                style="padding: 32px 0"
                v-else-if="mainView === 'write'"
                class="citation-text"
                v-html="summary"
              ></div>

              <div
                style="padding-bottom: 40px"
                class="journalistCol"
                v-else-if="mainView === 'discover'"
              >
                <div style="width: 100%" class="flex-end">
                  <div
                    @click="copyDiscoverText"
                    style="margin: 2px 0 0 4px"
                    class="image-container s-wrapper"
                  >
                    <img
                      style="cursor: pointer; filter: invert(40%)"
                      src="@/assets/images/clipboard.svg"
                      height="16px"
                      alt=""
                    />

                    <div class="s-tooltip">{{ copyTip }}</div>
                  </div>
                </div>
                <div class="journalistSection" v-for="(j, i) in discoverList" :key="i">
                  <p><span>Name</span>: {{ j.name }}</p>
                  <p><span>Publication</span>: {{ j.publication }}</p>
                  <p><span>Reason for selection</span>: {{ j.reason }}</p>
                  <button
                    :disabled="isViewOnly"
                    @click="grabJournalist(j.name, j.pub)"
                    class="secondary-button s-wrapper"
                  >
                    View bio
                    <div v-if="isViewOnly" class="s-tooltip">Locked</div>
                  </button>
                </div>
              </div>

              <!-- class="gradient-border-btm" -->
              <div
                class="row"
                style="margin: 8px 0 16px 0; padding-bottom: 24px"
                v-if="mainView !== 'write' && mainView !== 'discover'"
              >
                <button
                  v-if="!showingArticles"
                  @click="setOriginalArticles"
                  class="secondary-button-white fadein"
                  style="margin: 0"
                >
                  {{
                    mainView === 'news'
                      ? `Articles `
                      : mainView === 'social'
                      ? `Posts `
                      : mainView === 'web'
                      ? `Results`
                      : 'Sources'
                  }}

                  <div
                    v-if="mainView === 'news' || mainView === 'trending'"
                    style="margin-left: 4px"
                    class="row"
                  >
                    <img
                      v-for="(article, i) in articlesFiltered.slice(0, 3)"
                      :key="i"
                      :src="article.image_url ? article.image_url : article.image"
                      @error="onImageError($event)"
                      alt=""
                      class="circle-img"
                    />
                  </div>
                  <div v-else-if="mainView === 'web'" style="margin-left: 4px" class="row">
                    <img
                      v-for="(result, i) in filteredResults.slice(0, 3)"
                      :key="i"
                      :src="result.image"
                      @error="onImageError($event)"
                      alt=""
                      class="circle-img"
                    />
                  </div>

                  <div
                    v-else-if="mainView === 'social' && tweetMedia && tweetMedia.length"
                    style="margin-left: 4px"
                    class="row"
                    v-for="media in tweetMedia.slice(0, 3)"
                    :key="media.media_key"
                  >
                    <div>
                      <img
                        v-if="media.type === 'photo'"
                        :src="media.url"
                        @error="onImageError($event)"
                        class="circle-img"
                        alt=""
                      />

                      <video v-else-if="media.type === 'video'" class="circle-img" controls>
                        <source :src="media.variants[1].url" type="video/mp4" />
                      </video>

                      <video
                        v-else-if="media.type === 'animated_gif'"
                        class="circle-img"
                        autoplay
                        loop
                        muted
                        playsinline
                      >
                        <source :src="media.variants[0].url" type="video/mp4" />
                      </video>
                    </div>
                  </div>

                  <div v-else-if="mainView === 'social'" style="margin-left: 4px" class="row">
                    <img
                      v-for="(tweet, i) in filteredTweets.slice(0, 3)"
                      :key="i"
                      :src="tweet.image_url"
                      @error="onImageError($event)"
                      alt=""
                      class="circle-img"
                    />
                  </div>

                  <div v-else-if="mainView === 'omni'" style="margin-left: 4px" class="row">
                    <img
                      v-for="(article, i) in omniResults.slice(0, 3)"
                      :key="i"
                      :src="article.image_url ? article.image_url : logoPlaceholder"
                      @error="onImageError($event)"
                      alt=""
                      class="circle-img"
                    />
                  </div>
                </button>

                <button
                  v-else
                  @click="showingArticles = false"
                  class="secondary-button-white fadein"
                >
                  Hide
                  {{
                    mainView === 'news'
                      ? `Articles`
                      : mainView === 'social'
                      ? `Posts`
                      : mainView === 'web'
                      ? `Results`
                      : 'Sources'
                  }}
                </button>

                <div class="row" v-if="mainView === 'news' || mainView === 'social'">
                  <div
                    @click="toggleType(mainView === 'news' ? 'social' : 'news')"
                    class="s-wrapper"
                    style="margin: 0 12px; cursor: pointer"
                  >
                    <img
                      v-if="mainView === 'news'"
                      src="@/assets/images/thumb.svg"
                      height="16px"
                      alt=""
                    />
                    <img
                      v-else-if="mainView === 'social'"
                      src="@/assets/images/globe.svg"
                      height="16px"
                      alt=""
                    />
                    <div class="s-tooltip">
                      {{
                        isViewOnly
                          ? 'Locked'
                          : mainView === 'news'
                          ? 'Switch to Social'
                          : 'Switch to News'
                      }}
                    </div>
                  </div>

                  <div @click="toggleType('web')" style="cursor: pointer" class="s-wrapper">
                    <img src="@/assets/images/google.svg" height="16px" alt="" />
                    <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Switch to Web' }}</div>
                  </div>
                </div>

                <div class="row" v-if="mainView === 'web'">
                  <div
                    @click="toggleType('news')"
                    class="s-wrapper"
                    style="margin: 0 12px; cursor: pointer"
                  >
                    <img src="@/assets/images/globe.svg" height="16px" alt="" />
                    <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Switch to News' }}</div>
                  </div>

                  <div @click="toggleType('social')" style="cursor: pointer" class="s-wrapper">
                    <img src="@/assets/images/thumb.svg" height="16px" alt="" />
                    <div class="s-tooltip">
                      {{
                        isViewOnly
                          ? 'Locked'
                          : !hasTwitterIntegration
                          ? 'Connect Twiiter'
                          : 'Switch to Social'
                      }}
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="summaries.length">
                <div
                  style="padding: 24px 0"
                  class="gradient-border-top"
                  v-for="(summary, i) in summaries"
                  :key="i"
                  :ref="'summary-' + i"
                >
                  <div
                    style="width: 100%; justify-content: space-between; gap: 4px"
                    class="row"
                    v-if="
                      summary.clips.length &&
                      (mainView === 'news' || mainView === 'trending' || mainView === 'omni')
                    "
                  >
                    <div style="width: 24%" v-for="(clip, i) in summary.clips.slice(0, 4)" :key="i">
                      <img
                        @click="setAndShowArticles(summary.clips)"
                        :src="
                          clip.image_url
                            ? clip.image_url
                            : clip.image
                            ? clip.image
                            : logoPlaceholder
                        "
                        @error="onImageError($event)"
                        class="card-photo-header-small"
                      />
                    </div>
                  </div>

                  <div
                    v-else-if="summary.clips.length && mainView === 'web'"
                    style="margin-left: 4px"
                    class="row"
                  >
                    <div style="width: 24%" v-for="(clip, i) in summary.clips.slice(0, 4)" :key="i">
                      <img
                        @click="setAndShowArticles(summary.clips)"
                        :src="clip.image"
                        @error="onImageError($event)"
                        class="card-photo-header-small"
                      />
                    </div>
                  </div>

                  <div
                    v-else-if="summary.clips.length && mainView === 'social'"
                    style="width: 100%; justify-content: space-between; gap: 4px"
                    class="row"
                  >
                    <div
                      v-for="media in summary.media.slice(0, 4)"
                      :key="media.media_key"
                      style="width: 24%"
                    >
                      <img
                        v-if="media.type === 'photo'"
                        :src="media.url"
                        class="card-photo-header-small"
                        @error="onImageError($event)"
                        alt=""
                        @click="setAndShowArticles(summary.clips)"
                      />

                      <video
                        v-else-if="media.type === 'video'"
                        class="card-photo-header-small"
                        controls
                        @click="setAndShowArticles(summary.clips)"
                      >
                        <source :src="media.variants[1].url" type="video/mp4" />
                      </video>

                      <video
                        v-else-if="media.type === 'animated_gif'"
                        class="card-photo-header-small"
                        autoplay
                        loop
                        muted
                        playsinline
                        @click="setAndShowArticles(summary.clips)"
                      >
                        <source :src="media.variants[0].url" type="video/mp4" />
                      </video>
                    </div>
                  </div>

                  <h2 style="margin-top: 32px" class="ellipsis-text-bold">
                    {{ followUps[i] }}
                  </h2>
                  <div v-if="mainView !== 'discover'" style="position: relative">
                    <div
                      style="width: 100%"
                      class="space-between abs-container"
                      :class="{ lesserTop: mainView === 'write' }"
                    >
                      <div></div>

                      <div style="margin: 2px 0 0 4px" class="image-container s-wrapper">
                        <img
                          style="cursor: pointer; filter: invert(40%)"
                          src="@/assets/images/clipboard.svg"
                          height="16px"
                          alt=""
                          @click="copyTextAlt(summary.summary)"
                        />

                        <div class="s-tooltip">{{ copyTip }}</div>
                      </div>
                    </div>

                    <div
                      v-if="mainView === 'social'"
                      style="margin-top: 24px"
                      v-html="insertAltTweetCitations(summary.summary, i)"
                      class="citation-text"
                    ></div>

                    <div
                      v-else-if="mainView === 'omni'"
                      style="margin-top: 24px"
                      v-html="insertAltOmniCitations(summary.summary, i)"
                      class="citation-text"
                    ></div>

                    <div
                      v-else-if="mainView !== 'web'"
                      style="margin-top: 24px"
                      v-html="insertAltNewsCitations(summary.summary, i)"
                      class="citation-text"
                    ></div>

                    <div
                      v-else
                      style="margin-top: 24px"
                      v-html="insertAltWebCitations(summary.summary, i)"
                      class="citation-text"
                    ></div>
                  </div>

                  <div style="padding-bottom: 40px" class="journalistCol" v-else>
                    <div style="width: 100%" class="flex-end">
                      <div></div>

                      <div style="margin: 2px 0 0 4px" class="image-container s-wrapper">
                        <img
                          style="cursor: pointer; filter: invert(40%)"
                          src="@/assets/images/clipboard.svg"
                          height="16px"
                          alt=""
                          @click="copyDiscoverTextAlt(summary.list)"
                        />

                        <div class="s-tooltip">{{ copyTip }}</div>
                      </div>
                    </div>

                    <div v-for="(j, i) in summary.list" :key="i" class="journalistSection">
                      <p><span>Name</span>: {{ j.name }}</p>
                      <p><span>Publication</span>: {{ j.publication }}</p>
                      <p><span>Reason for selection</span>: {{ j.reason }}</p>
                      <button
                        :disabled="isViewOnly"
                        @click="grabJournalist(j.name, j.pub)"
                        class="secondary-button s-wrapper"
                      >
                        View bio
                        <div v-if="isViewOnly" class="s-tooltip">Locked</div>
                      </button>
                    </div>
                  </div>

                  <button
                    v-if="
                      !showingArticles &&
                      summary.clips.length &&
                      (mainView === 'news' ||
                        mainView === 'trending' ||
                        mainView === 'web' ||
                        mainView === 'social' ||
                        mainView === 'omni')
                    "
                    @click="setAndShowArticles(summary.clips)"
                    class="secondary-button-white fadein"
                    style="margin: 0"
                  >
                    {{
                      mainView === 'news' || mainView === 'trending'
                        ? `Articles `
                        : mainView === 'social'
                        ? `Posts `
                        : mainView === 'omni'
                        ? `Sources `
                        : `Results`
                    }}

                    <div
                      v-if="mainView === 'news' || mainView === 'trending' || mainView === 'omni'"
                      style="margin-left: 4px"
                      class="row"
                    >
                      <img
                        v-for="(article, i) in summary.clips.slice(0, 3)"
                        :key="i"
                        :src="
                          article.image_url
                            ? article.image_url
                            : article.image
                            ? article.image
                            : logoPlaceholder
                        "
                        alt=""
                        class="circle-img"
                      />
                    </div>

                    <div v-else-if="mainView === 'web'" style="margin-left: 4px" class="row">
                      <img
                        v-for="(result, i) in summary.clips.slice(0, 3)"
                        :key="i"
                        :src="result.image"
                        alt=""
                        class="circle-img"
                      />
                    </div>

                    <div
                      v-else-if="mainView === 'social' && summary.media"
                      style="margin-left: 4px"
                      class="row"
                      v-for="media in summary.media.slice(0, 3)"
                      :key="media.media_key"
                    >
                      <div>
                        <img
                          v-if="media.type === 'photo'"
                          :src="media.url"
                          class="circle-img"
                          alt=""
                        />

                        <video v-else-if="media.type === 'video'" class="circle-img" controls>
                          <source :src="media.variants[1].url" type="video/mp4" />
                        </video>

                        <video
                          v-else-if="media.type === 'animated_gif'"
                          class="circle-img"
                          autoplay
                          loop
                          muted
                          playsinline
                        >
                          <source :src="media.variants[0].url" type="video/mp4" />
                        </video>
                      </div>
                    </div>

                    <div
                      v-else-if="mainView === 'social'"
                      style="margin-left: 4px"
                      class="row"
                      v-for="(result, i) in summary.clips.slice(0, 3)"
                      :key="i"
                    >
                      <img :src="result.image" alt="" class="circle-img" />
                    </div>
                  </button>

                  <button
                    v-else-if="summary.clips.length && (mainView === 'news' || mainView === 'web')"
                    @click="showingArticles = false"
                    class="secondary-button-white fadein"
                  >
                    Hide
                    {{
                      mainView === 'news'
                        ? `Articles (${articlesFiltered.length})`
                        : mainView === 'social'
                        ? `Posts (${filteredTweets.length})`
                        : `Results (${googleResults.length})`
                    }}
                  </button>
                  <div style="margin-top: 32px" v-else></div>
                </div>
              </div>

              <div style="margin-top: 32px; width: 100%" v-if="secondaryLoader">
                <div class="row">
                  <p style="margin: 0; margin-right: 8px" class="bold-text">Generating...</p>
                  <img
                    class="rotation innvert"
                    height="14px"
                    src="@/assets/images/loading.svg"
                    alt=""
                  />
                </div>

                <div style="width: 100%; margin-top: 24px" class="col">
                  <div class="skeleton skeleton-title"></div>
                  <div class="skeleton skeleton-text"></div>
                  <div class="skeleton skeleton-text"></div>
                </div>
              </div>

              <div style="margin-top: 32px; width: 100%" v-else-if="secondaryLoaderAlt">
                <div class="row">
                  <p
                    v-if="mainView === 'news'"
                    style="margin: 0; margin-right: 8px"
                    class="bold-text"
                  >
                    Gathering news...
                  </p>
                  <p
                    v-else-if="mainView === 'trending'"
                    style="margin: 0; margin-right: 8px"
                    class="bold-text"
                  >
                    Gathering trending news...
                  </p>
                  <p
                    v-else-if="mainView === 'social'"
                    style="margin: 0; margin-right: 8px"
                    class="bold-text"
                  >
                    Scanning social posts...
                  </p>
                  <p
                    v-else-if="mainView === 'omni'"
                    style="margin: 0; margin-right: 8px"
                    class="bold-text"
                  >
                    Searching...
                  </p>
                  <p v-else style="margin: 0; margin-right: 8px" class="bold-text">
                    Scanning the web...
                  </p>
                  <img
                    class="rotation innvert"
                    height="14px"
                    src="@/assets/images/loading.svg"
                    alt=""
                  />
                </div>

                <div
                  v-if="mainView !== 'omni'"
                  style="margin-top: 24px; justify-content: space-between"
                  class="row"
                >
                  <div style="width: 23.5%" class="skeleton skeleton-img"></div>
                  <div style="width: 23.5%" class="skeleton skeleton-img"></div>
                  <div style="width: 23.5%" class="skeleton skeleton-img"></div>
                  <div style="width: 23.5%" class="skeleton skeleton-img"></div>
                </div>

                <div style="margin-left: 3px" v-else>
                  <div :class="{ opaquer: searchingType !== 'news' }" class="omni-load">
                    <div :class="{ pulse: searchingType === 'news' }" class="row">
                      <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                      <p class="bold-text">Searching thousands of news outlets</p>
                    </div>

                    <p
                      class="bold-text fadein"
                      style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                      v-if="searchingType === 'news'"
                    >
                      Reading ...
                    </p>

                    <div style="margin-left: 24px" class="fadein row" v-if="altOmniNews.length">
                      <button
                        style="margin-right: 8px"
                        class="secondary-button fadein"
                        v-for="(article, i) in altOmniNews.slice(0, 4)"
                        :key="i"
                      >
                        <img
                          :src="article.image_url ? article.image_url : logoPlaceholder"
                          height="12px"
                          alt=""
                          style="margin: 0 8px 0 1px"
                        />

                        {{ article.source.name }}
                      </button>
                    </div>
                  </div>

                  <div :class="{ opaquer: searchingType !== 'social' }" class="omni-load">
                    <div :class="{ pulse: searchingType === 'social' }" class="row">
                      <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                      <p class="bold-text">Sifting through top social media posts</p>
                    </div>

                    <p
                      class="bold-text fadein"
                      style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                      v-if="searchingType === 'social'"
                    >
                      Reading ...
                    </p>

                    <div style="margin-left: 24px" class="fadein row" v-if="altOmniSocial.length">
                      <button
                        style="margin-right: 8px"
                        class="secondary-button fadein"
                        v-for="(article, i) in altOmniSocial.slice(0, 4)"
                        :key="i"
                      >
                        <img
                          v-if="article.type === 'youtube'"
                          :src="youtubePlaceholder"
                          height="12px"
                          alt=""
                          style="margin: 0 8px 0 1px"
                        />
                        <img
                          v-else-if="article.type === 'bluesky'"
                          :src="blueskyPlaceholder"
                          height="14px"
                          alt=""
                          style="margin: 0 8px 0 1px"
                        />
                        <img
                          v-else-if="article.type === 'twitter'"
                          :src="twitterPlaceholder"
                          height="12px"
                          alt=""
                          style="margin: 0 8px 0 1px"
                        />

                        <div v-if="article.type === 'twitter'">{{ article.user.username }}</div>
                        <div v-else>{{ article.author }}</div>
                      </button>
                    </div>
                  </div>

                  <div :class="{ opaquer: searchingType !== 'web' }" class="omni-load">
                    <div :class="{ pulse: searchingType === 'web' }" class="row">
                      <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                      <p class="bold-text">Scouring the web</p>
                    </div>

                    <p
                      class="bold-text fadein"
                      style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                      v-if="searchingType === 'web'"
                    >
                      Reading ...
                    </p>

                    <div style="margin-left: 24px" class="fadein row" v-if="altOmniWeb.length">
                      <button
                        style="margin-right: 8px"
                        class="secondary-button fadein"
                        v-for="(article, i) in altOmniWeb.slice(0, 4)"
                        :key="i"
                      >
                        <img
                          :src="
                            article.source && article.source_img
                              ? article.source_img
                              : globePlaceholder
                          "
                          height="12px"
                          alt=""
                          style="margin: 0 8px 0 1px"
                        />
                        <small>{{ article.source }}</small>
                      </button>
                    </div>
                  </div>

                  <div :class="{ opaquer: searchingType !== 'summary' }" class="omni-load">
                    <div :class="{ pulse: searchingType === 'summary' }" class="row">
                      <img class="pulse-dot" src="@/assets/images/dot.svg" height="14px" alt="" />
                      <p class="bold-text">Generating summary</p>
                    </div>

                    <!-- <p
                      class="bold-text fadein"
                      style="margin: 0 0 16px 28px; color: #aaaaaa; font-size: 14px"
                      v-if="searchingType === 'summary'"
                    >
                      Summarizing ...
                    </p> -->

                    <div
                      style="padding: 8px 0 0 0; margin-left: 24px"
                      class="skeleton-loader fadein"
                    >
                      <div
                        v-if="searchingType === 'summary'"
                        style="margin-bottom: 16px"
                        class="skeleton skeleton-title"
                      ></div>

                      <div v-if="searchingType === 'summary'" class="skeleton skeleton-text"></div>
                      <div v-if="searchingType === 'summary'" class="skeleton skeleton-text"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>

      <div
        v-if="!loading && !summaryLoading && !isViewOnly"
        style="
          background: white;
          position: sticky;
          bottom: 32px;
          margin: 40px auto;
          border-radius: 20px;
          padding: 8px 0;
          width: 60vw;
          transition: margin 0.5s ease-in-out;
          transition: width 0.5s ease-in-out;
        "
        :class="['input-container-gray fadein', { contentShift: showingArticles }]"
      >
        <section>
          <div style="margin: 8px 0 0 0; width: 100%" class="row">
            <textarea
              ref="textarea"
              style="max-height: 140px !important; padding-top: 0.25rem"
              class="area-input"
              :placeholder="
                mainView === 'discover'
                  ? 'Generate a new list...'
                  : mainView === 'write'
                  ? 'Regenerate or create new content...'
                  : 'Ask follow-up...'
              "
              autofocus
              autocomplete="off"
              rows="1"
              v-model="newTemplate"
              :disabled="loading || summaryLoading"
              @keyup.enter="
                mainView === 'news' || mainView === 'trending'
                  ? getChatSummary($event, filteredArticles, newTemplate)
                  : mainView === 'social'
                  ? getChatSummary($event, preparedTweets, newTemplate)
                  : mainView === 'omni'
                  ? getChatSummary($event, omniResults, newTemplate)
                  : mainView === 'write'
                  ? regeneratePitch($event)
                  : getChatSummary($event, googleResults, newTemplate)
              "
              v-autoresize
            />

            <div
              v-if="newTemplate"
              @click="
                mainView === 'news' || mainView === 'trending'
                  ? getChatSummary($event, filteredArticles, newTemplate)
                  : mainView === 'social'
                  ? getChatSummary($event, preparedTweets, newTemplate)
                  : mainView === 'omni'
                  ? getChatSummary($event, omniResults, newTemplate)
                  : mainView === 'write'
                  ? regeneratePitch($event)
                  : getChatSummary($event, googleResults, newTemplate)
              "
              class="left-margin pointer lite-bg img-container-stay"
              style="margin-right: 12px; padding: 5px 7px 4px 9px"
            >
              <img
                style="margin: 0"
                src="@/assets/images/paper-plane-full.svg"
                height="12px"
                alt=""
              />
            </div>

            <div
              v-else
              class="left-margin pointer img-container-stay"
              style="margin-right: 12px; padding: 5px 7px 4px 9px"
            >
              <img
                style="margin: 0"
                src="@/assets/images/paper-plane-full.svg"
                height="12px"
                alt=""
              />
            </div>
          </div>

          <div style="padding: 4px 8px" class="row">
            <!-- :class="{ 'soft-gray-bg': showingSources }" -->
            <div style="margin: 12px 12px 0 8px" class="source-dropdown fadein">
              <div
                @click.stop="toggleSources"
                class="drop-header s-wrapper"
                style="padding: 5px 10px 5px 4px; background"
              >
                <img
                  v-if="mainView === 'write'"
                  src="@/assets/images/edit.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else-if="mainView === 'news'"
                  src="@/assets/images/globe.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else-if="mainView === 'social'"
                  src="@/assets/images/thumb.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else-if="mainView === 'web'"
                  src="@/assets/images/google.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else-if="mainView === 'discover'"
                  src="@/assets/images/users.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else-if="mainView === 'trending'"
                  src="@/assets/images/arrow-trend-up.svg"
                  height="11px"
                  alt=""
                />
                <img
                  v-else-if="mainView === 'omni'"
                  src="@/assets/images/brain.svg"
                  height="15px"
                  alt=""
                />

                <small>{{ mainView === 'discover' ? 'Contacts' : toCamelCase(mainView) }}</small>

                <div class="s-tooltip">Mode</div>
              </div>

              <div
                v-outside-click="hideSources"
                v-show="showingSources"
                class="drop-options-alt-up"
              >
                <header>
                  <h4>Mode</h4>

                  <p>Select the type of task you'd like ManagrAI to assist with</p>
                </header>
                <section>
                  <div
                    @click="switchMainView('omni')"
                    :class="{ activeswitch: mainView === 'discover' }"
                  >
                    <span>
                      <img src="@/assets/images/brain.svg" height="11px" alt="" />
                      Omni
                    </span>

                    <p>Search news, social and web</p>
                  </div>

                  <div
                    @click="switchMainView('news')"
                    :class="{ activeswitch: mainView === 'news' }"
                  >
                    <span>
                      <img src="@/assets/images/globe.svg" height="11px" alt="" />
                      News
                    </span>
                    <p>Search real-time news</p>
                  </div>

                  <div
                    @click="switchMainView('social')"
                    :class="{ activeswitch: mainView === 'social' }"
                  >
                    <span>
                      <img src="@/assets/images/thumb.svg" height="11px" alt="" />
                      Social
                    </span>

                    <p>Search top social posts</p>
                  </div>

                  <div @click="switchMainView('web')" :class="{ activeswitch: mainView === 'web' }">
                    <span>
                      <img src="@/assets/images/google.svg" height="11px" alt="" />
                      Web
                    </span>

                    <p>Search the web</p>
                  </div>

                  <!-- <div
                    @click="switchMainView('trending')"
                    :class="{ activeswitch: mainView === 'trending' }"
                  >
                    <span>
                      <img src="@/assets/images/arrow-trend-up.svg" height="11px" alt="" />
                      Trending
                    </span>

                    <p>Search trending news</p>
                  </div> -->

                  <div
                    @click="switchMainView('write')"
                    :class="{ activeswitch: mainView === 'write' }"
                  >
                    <span>
                      <img src="@/assets/images/edit.svg" height="11px" alt="" />
                      Write
                    </span>

                    <p>Generate content or get responses without scanning the news</p>
                  </div>

                  <div
                    @click="toggleContactsModal"
                    :class="{ activeswitch: mainView === 'discover' }"
                  >
                    <span>
                      <img src="@/assets/images/users.svg" height="11px" alt="" />
                      Media Contacts
                    </span>

                    <p>Search media contacts</p>
                  </div>
                </section>
              </div>
            </div>

            <div
              style="margin-right: 12px"
              v-if="mainView !== 'discover'"
              class="source-dropdown fadein"
            >
              <div
                @click.stop="toggleMainDetails"
                :class="
                  detailTitle
                    ? 'drop-header padding-right-x s-wrapper'
                    : 'image-container s-wrapper'
                "
              >
                <img src="@/assets/images/folder.svg" height="15px" alt="" />
                <small v-if="detailTitle" :title="detailTitle">{{ detailTitle }}</small>
                <div class="image-container abs-right-img" @click="clearDetails" v-if="detailTitle">
                  <img src="@/assets/images/close.svg" height="12px" alt="" />
                </div>

                <div class="s-tooltip">Projects</div>
              </div>

              <div
                v-outside-click="hideMainDetails"
                v-if="showingMainDetails"
                class="drop-options-alt-up left-mobile"
              >
                <header>
                  <h4>Projects</h4>
                  <p>Let ManagrAI know what you're working on (e.g. campaign, pitch, launch)</p>
                  <!-- <button
                            @click="toggleDetailsInputModal"
                            class="secondary-button-no-border"
                            style="margin-right: 4px"
                          >
                            <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Details
                          </button> -->
                </header>
                <!-- <header style="padding-top: 8px; padding-bottom: 8px" class="space-between">
                  <button
                    @click="toggleDetailsInputModal"
                    class="secondary-button-no-border"
                    style="margin-right: 4px"
                  >
                    <img src="@/assets/images/add.svg" height="14px" alt="" /> Add Details
                  </button>

                  <button
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
                  </button>
                </header> -->

                <section v-if="allCompanyDetails.length && !editingProjects">
                  <div
                    style="position: relative"
                    @click="addDetails(detail.title, detail.details)"
                    v-for="detail in allCompanyDetails"
                    :key="detail.title"
                    :class="{ activesquareTile: detailTitle === detail.title }"
                    :title="detail.title"
                  >
                    <span style="max-width: 140px" class="ellipsis-text-s">
                      {{ detail.title }}
                    </span>
                    <p class="">{{ detail.details }}</p>

                    <span @click="deleteCompanyDetails(detail.id)" class="absolute-icon">
                      <img src="@/assets/images/close.svg" height="10px" alt="" />
                    </span>
                  </div>
                </section>

                <section v-else-if="editingProjects">
                  <textarea
                    v-model="selectedProject.details"
                    rows="3"
                    class="area-input text-area-input"
                    :class="{ opaquest: loadingPitch }"
                    v-autoresize
                    :placeholder="selectedProject.details"
                    style="
                      border: 1px solid rgba(0, 0, 0, 0.1) !important;
                      border-radius: 8px;
                      padding: 16px 8px;
                    "
                    maxlength="800"
                  ></textarea>
                </section>

                <section style="padding: 16px" v-else>
                  Your saved projects
                  <span>
                    <img
                      style="margin-right: 4px"
                      src="@/assets/images/folder.svg"
                      height="12px"
                      alt=""
                    />
                    will appear here.</span
                  >
                </section>

                <footer v-if="!editingProjects" class="space-between">
                  <span></span>
                  <button
                    @click="toggleDetailsInputModal"
                    class="primary-button"
                    style="margin-right: 4px"
                  >
                    Add Project
                  </button>
                </footer>

                <footer v-else class="space-between">
                  <button
                    @click="deleteCompanyDetails(selectedProject.id)"
                    class="primary-button pinkbg"
                  >
                    Delete
                  </button>

                  <main class="row">
                    <button @click="editingProjects = false" class="secondary-button">
                      Cancel
                    </button>
                    <button @click="updateProject" class="primary-button">Update</button>
                  </main>
                </footer>
              </div>
            </div>

            <div
              style="margin-right: 12px"
              v-if="mainView === 'write'"
              class="source-dropdown fadein"
            >
              <div @click.stop="toggleShowStyles" class="drop-header s-wrapper">
                <img src="@/assets/images/wand.svg" height="15px" alt="" />

                <small>{{ writingStyleTitle ? writingStyleTitle : 'Voice' }}</small>
                <div class="s-tooltip">Voices</div>
              </div>

              <div
                v-outside-click="hideStyles"
                v-show="showingStyles"
                class="drop-options-alt-up left-mobile"
                style="bottom: 48px"
              >
                <header>
                  <!-- <section class="h-padding">
                            <section @click="toggleStyles" class="toggle">
                              <span
                                :class="{ 'active-toggle': personalStyles }"
                                class="toggle-side"
                              >
                                <small>Personal</small>
                              </span>

                              <span
                                :class="{ 'active-toggle': !personalStyles }"
                                class="toggle-side"
                              >
                                <small>Group</small>
                              </span>
                            </section>
                          </section> -->

                  <h4>Voices</h4>
                  <p>Select a desired writing style or create your own</p>

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
                      {{ style.title }}
                    </span>
                    <p>{{ style.style }}</p>
                  </div>
                  <div
                    @mouseenter="setIndex(i)"
                    @mouseLeave="removeIndex"
                    @click="addWritingStyle(style.style, style.title)"
                    class="dropdown-item relative"
                    v-for="(style, i) in userWritingStyles"
                    :key="i"
                    :class="{ activeswitch: writingStyleTitle === style.title }"
                    :title="style.title"
                  >
                    <span>
                      {{ style.title }}
                    </span>
                    <p>{{ style.style }}</p>

                    <span
                      v-if="hoverIndex === i"
                      @click="deleteWritingStyle(style.id)"
                      class="absolute-icon"
                    >
                      <img src="@/assets/images/close.svg" height="12px" alt="" />
                    </span>
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

                <footer class="space-between">
                  <span></span>
                  <button
                    @click="toggleLearnInputModal('')"
                    class="primary-button"
                    style="margin-right: 12px"
                  >
                    Create
                  </button>
                </footer>
              </div>
            </div>

            <div
              v-if="mainView === 'news' || mainView === 'social' || mainView === 'omni'"
              class="row relative top-mar-mobile"
            >
              <div
                @click.stop="toggleDate"
                :class="{ 'soft-gray-bg': showDateSelection }"
                class="image-container s-wrapper"
              >
                <img class="invert" src="@/assets/images/calendar.svg" height="15px" alt="" />

                <div class="s-tooltip">{{ isViewOnly ? 'Locked' : 'Date' }}</div>
              </div>

              <div
                v-outside-click="hideDate"
                class="container-left-above left-mobile"
                v-show="showDateSelection"
              >
                <header>
                  <p>Date Range</p>
                </header>

                <div style="margin-top: 16px" class="row">
                  <input
                    class="area-input-smallest"
                    type="date"
                    :min="mainView === 'news' ? minDate : minDateSocial"
                    @input="validateDate"
                    v-model="dateStart"
                  />
                  <span style="margin: 0 12px"> - </span>

                  <input
                    class="area-input-smallest"
                    type="date"
                    :min="mainView === 'news' ? minDate : minDateSocial"
                    v-model="dateEnd"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div style="width: 100vw; height: 100vh" v-if="selectedSearch">
      <div v-if="showingAnalytics" style="position: relative">
        <div class="containered">
          <div v-if="loadingAnalytics" style="position: relative" class="containered__top">
            <div @click="showingAnalytics = false" class="image-container abs-top-right">
              <img src="@/assets/images/close.svg" height="16px" alt="" />
            </div>
            <div style="margin-bottom: 12px">
              <img
                :src="
                  currentArticle.hasOwnProperty('snippet')
                    ? currentArticle.image
                    : currentArticle.image_url
                "
                class="photo-header-small"
              />
            </div>

            <div style="padding: 12px 0" class="row">
              <p style="margin: 0; margin-right: 8px; font-size: 14px" class="bold-text">
                Analyzing article...
              </p>
              <img
                class="rotation innvert"
                height="14px"
                src="@/assets/images/loading.svg"
                alt=""
              />
            </div>
          </div>

          <div v-else style="position: relative" class="containered__top">
            <div style="position: sticky; top: 0">
              <div @click="showingAnalytics = false" class="image-container abs-top-right">
                <img src="@/assets/images/close.svg" height="16px" alt="" />
              </div>
            </div>

            <div
              v-if="
                mainView === 'web' ||
                mainView === 'news' ||
                (mainView === 'omni' && !currentArticle.hasOwnProperty('type'))
              "
              style="margin-bottom: 12px"
            >
              <img
                @error="onImageError($event)"
                :src="currentArticle.image_url"
                class="photo-header-small"
              />
            </div>

            <div v-else style="margin-bottom: 12px">
              <iframe
                v-if="currentArticle.type === 'youtube'"
                :src="`https://www.youtube.com/embed/${currentArticle.id}`"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                width="100%"
                height="360"
              ></iframe>

              <img
                v-else
                @error="onImageError($event)"
                :src="currentArticle.image_url ? currentArticle.image_url : blueskyPlaceholder"
                class="photo-header-small"
              />
            </div>

            <div class="space-between-top no-letter-margin">
              <div class="col">
                <p
                  v-if="
                    mainView === 'web' ||
                    mainView === 'news' ||
                    (mainView === 'omni' && !currentArticle.hasOwnProperty('type'))
                  "
                  style="margin: 0"
                  class="bold-font"
                >
                  {{
                    currentArticle.traffic ? removeDomain(currentArticle.traffic.target) : 'unknown'
                  }}
                </p>

                <p v-else style="margin: 0" class="bold-font">
                  {{ currentArticle.type === 'youtube' ? 'YouTube' : 'Bluesky' }}
                </p>

                <div style="margin-top: 8px; color: #3b8ec0" class="row">
                  <span>by</span>
                  <p style="font-size: 14px; margin-left: 2px">{{ currentArticle.author }}</p>
                </div>
              </div>
              <small
                v-if="
                  mainView === 'web' ||
                  mainView === 'news' ||
                  (mainView === 'omni' && !currentArticle.hasOwnProperty('type'))
                "
                >{{ getTimeDifferenceInMinutes(currentArticle.publish_date) }}</small
              >
              <small v-else>{{ getTimeDifferenceInMinutes(currentArticle.created_at) }}</small>
            </div>

            <div>
              <div class="elipsis-text" style="margin: 10px 0; font-size: 15px; line-height: 24px">
                <a
                  v-if="
                    mainView === 'web' ||
                    mainView === 'news' ||
                    (mainView === 'omni' && !currentArticle.hasOwnProperty('type'))
                  "
                  :href="currentArticle.link"
                  target="_blank"
                  class="bold-txt a-text"
                >
                  {{ currentArticle.title }}
                </a>
                <a v-else :href="currentArticle.url" target="_blank" class="bold-txt a-text">
                  {{
                    currentArticle.title
                      ? currentArticle.title
                      : currentArticle.traffic
                      ? currentArticle.traffic.description
                      : 'View Post'
                  }}
                </a>
              </div>
            </div>

            <div
              v-if="
                mainView === 'web' ||
                mainView === 'news' ||
                (mainView === 'omni' && !currentArticle.hasOwnProperty('type'))
              "
              class="space-between bottom-margin-m"
            >
              <div class="row img-mar">
                <img src="@/assets/images/users.svg" height="12px" alt="" />
                <p style="font-size: 14px" class="bold-font">
                  {{ currentArticle.traffic ? formatNumberAlt(currentArticle.traffic.users) : 0 }}
                </p>
              </div>

              <section class="row img-mar img-mar">
                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/facebook.png" height="12px" alt="" />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      formatNumberAlt(
                        currentArticle.social[0]
                          ? currentArticle.social[0]['total_facebook_shares']
                          : 0,
                      )
                    }}
                  </p>
                </div>

                <div style="margin-right: 12px" class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/twitter-x.svg"
                    height="12px"
                    alt=""
                  />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      formatNumberAlt(
                        currentArticle.social[0] ? currentArticle.social[0]['twitter_shares'] : 0,
                      )
                    }}
                  </p>
                </div>

                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/reddit.svg" height="12px" alt="" />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      formatNumberAlt(
                        currentArticle.social[0]
                          ? currentArticle.social['total_reddit_engagements']
                          : 0,
                      )
                    }}
                  </p>
                </div>

                <div class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/pinterest.png"
                    height="12px"
                    alt=""
                  />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      formatNumberAlt(
                        currentArticle.social[0] ? currentArticle.social[0]['pinterest_shares'] : 0,
                      )
                    }}
                  </p>
                </div>
              </section>
            </div>

            <div
              v-else-if="currentArticle.type === 'youtube'"
              class="space-between bottom-margin-m"
            >
              <div class="row img-mar">
                <img src="@/assets/images/users.svg" height="12px" alt="" />
                <p style="font-size: 14px" class="bold-font">
                  {{
                    currentArticle.traffic ? formatNumberAlt(currentArticle.traffic.viewCount) : 0
                  }}
                </p>
              </div>

              <section class="row img-mar img-mar">
                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/thumb.svg" height="12px" alt="" />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      currentArticle.traffic ? formatNumberAlt(currentArticle.traffic.likeCount) : 0
                    }}
                  </p>
                </div>

                <div style="margin-right: 12px" class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/heart.svg"
                    height="12px"
                    alt=""
                  />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      currentArticle.traffic
                        ? formatNumberAlt(currentArticle.traffic.favoriteCount)
                        : 0
                    }}
                  </p>
                </div>

                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/comment.svg" height="12px" alt="" />
                  <p style="font-size: 14px" class="bold-font">
                    {{
                      currentArticle.traffic
                        ? formatNumberAlt(currentArticle.traffic.commentCount)
                        : 0
                    }}
                  </p>
                </div>
              </section>
            </div>

            <div
              v-else-if="currentArticle.type === 'bluesky'"
              class="space-between bottom-margin-m"
            >
              <div class="row img-mar">
                <img src="@/assets/images/users.svg" height="12px" alt="" />
                <p style="font-size: 14px" class="bold-font">
                  {{
                    currentArticle.traffic
                      ? formatNumberAlt(currentArticle.traffic.followersCount)
                      : 0
                  }}
                </p>
              </div>

              <section class="row img-mar img-mar">
                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/heart.svg" height="12px" alt="" />
                  <p style="font-size: 14px" class="bold-font">
                    {{ currentArticle.stats ? formatNumberAlt(currentArticle.stats.likes) : 0 }}
                  </p>
                </div>

                <div style="margin-right: 12px" class="row">
                  <img src="@/assets/images/commentAlt.svg" height="12px" alt="" />
                  <p style="font-size: 14px" class="bold-font">
                    {{ currentArticle.stats ? formatNumberAlt(currentArticle.stats.replies) : 0 }}
                  </p>
                </div>

                <div style="margin-right: 12px" class="row">
                  <img
                    style="margin-right: 4px"
                    src="@/assets/images/arrows-retweet.svg"
                    height="12px"
                    alt=""
                  />
                  <p style="font-size: 14px" class="bold-font">
                    {{ currentArticle.stats ? formatNumberAlt(currentArticle.stats.reposts) : 0 }}
                  </p>
                </div>
              </section>
            </div>
          </div>

          <div
            v-if="
              mainView === 'social' ||
              (mainView === 'omni' && currentArticle.hasOwnProperty('type'))
            "
          >
            <p class="bold-text">Description:</p>
            <div style="margin-top: 12px; font-size: 15px !important">
              <p>{{ currentArticle.text ? currentArticle.text : 'None' }}</p>
            </div>
          </div>

          <div v-if="currentArticle.summary">
            <div
              style="margin-top: 12px; font-size: 15px !important"
              v-html="currentArticle.summary"
              class="pre-text"
            ></div>
          </div>

          <div v-if="loadingAnalytics">
            <div style="margin-top: 12px"></div>
          </div>
        </div>
      </div>

      <div
        v-if="summary && showingArticles && mainView !== 'write'"
        :class="['sidebar-aside fadein', { open: showingArticles }]"
      >
        <div
          style="
            padding: 0 16px;
            position: sticky;
            top: 24px;
            z-index: 100;
            background-color: white;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
          "
          class="space-between"
        >
          <p class="bold-text">
            {{
              mainView === 'news' || mainView === 'trending'
                ? `Articles (${sidebarArticles.length})`
                : mainView === 'social'
                ? `Posts (${sidebarArticlesSocial.length})`
                : mainView === 'web'
                ? `Results (${sidebarArticlesWeb.length})`
                : `Sources (${sidebarArticlesOmni.length})`
            }}
          </p>

          <div @click="showingArticles = false" class="image-container">
            <img src="@/assets/images/close.svg" height="16px" alt="" />
          </div>
        </div>

        <div class="section">
          <div v-if="mainView === 'news' || mainView === 'trending'" class="cards-container">
            <div v-for="(article, i) in sidebarArticles" :key="article.id" class="card">
              <div style="width: 100%">
                <div class="main-body">
                  <div>
                    <div style="margin: 0 0 4px -2px" class="row">
                      <!-- src="@/assets/images/iconlogo.png" -->
                      <img
                        :src="
                          article.source && article.source.icon
                            ? article.source.icon
                            : globePlaceholder
                        "
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <small>{{
                        mainView === 'trending'
                          ? article.source
                              .replace(/^https?:\/\//, '')
                              .replace(/^www\./, '')
                              .replace('.com', '')
                          : article.source.name
                      }}</small>
                    </div>

                    <p
                      style="cursor: pointer"
                      @click="goToArticle(mainView === 'trending' ? article.url : article.link)"
                    >
                      {{ article.title }}
                    </p>
                    <div style="border-bottom: none; font-size: 14px; color: #484a6e" class="row">
                      <p class="thin-text">
                        <span
                          >{{
                            getTimeDifferenceInMinutes(
                              mainView === 'trending' ? article.date : article.publish_date,
                            )
                          }}
                        </span>
                        -
                        {{ article.description }}
                      </p>
                    </div>
                  </div>

                  <div>
                    <img
                      @click="goToArticle(mainView === 'trending' ? article.url : article.link)"
                      :src="mainView === 'trending' ? article.image : article.image_url"
                      @error="onImageError($event)"
                      class="card-photo-header"
                    />
                  </div>
                </div>
                <div class="space-between" style="margin: -4px 0 0 10px">
                  <p @click="selectJournalist(article)" class="turq-text">
                    By <span>{{ extractJournalist(article.author) }}</span>
                  </p>

                  <button
                    @click="getTrafficData(article.url ? article.url : article.link, article)"
                    style="margin-right: 16px"
                    class="secondary-button alt-btn s-wrapper"
                    :disabled="isViewOnly"
                  >
                    <img
                      style="margin-right: 8px"
                      src="@/assets/images/sparkle.svg"
                      height="12px"
                      alt=""
                    />
                    Analyze

                    <div v-if="isViewOnly" class="s-tooltip">Locked</div>
                  </button>
                </div>
                <!-- <div v-if="articlesShowingDetails.includes(i)" style="margin: 8px" class="row">
                  <button
                    @click="selectJournalist(article)"
                    style="font-size: 10px; margin-right: 8px"
                    class="secondary-button-white"
                  >
                    Journalist Bio
                  </button>
                  <button
                    @click="getArticleSummary(article.link)"
                    style="font-size: 10px"
                    class="secondary-button-white"
                  >
                    Article Insights
                  </button>
                </div>

                <div
                  v-else
                  @click="toggleArticleActions(i)"
                  style="margin: 4px 0 0 8px; cursor: pointer; width: fit-content"
                >
                  <img
                    src="@/assets/images/more_horizontal.svg"
                    height="auto"
                    width="22px"
                    alt=""
                  />
                </div> -->
              </div>
            </div>
          </div>

          <div v-else-if="mainView === 'web'" class="cards-container">
            <div v-for="(result, i) in sidebarArticlesWeb" :key="i" class="card">
              <div style="width: 100%">
                <div class="main-body">
                  <div>
                    <div style="margin: 0 0 4px -2px" class="row">
                      <img
                        :src="
                          result.source && result.source_img ? result.source_img : globePlaceholder
                        "
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <small>{{ result.source }}</small>
                    </div>

                    <p style="cursor: pointer" @click="goToArticle(result.link)">
                      {{ result.title }}
                    </p>
                    <div style="border-bottom: none; font-size: 14px; color: #484a6e" class="row">
                      <p class="thin-text">
                        {{ result.snippet }}
                      </p>
                    </div>
                  </div>

                  <div>
                    <img
                      @click="goToArticle(result.link)"
                      :src="result.image"
                      @error="onImageError($event)"
                      class="card-photo-header"
                    />
                  </div>
                </div>
                <div style="margin: -4px 0 0 10px">
                  <p @click="selectJournalist(result, true)" class="turq-text">
                    By <span>{{ result.author }}</span>
                  </p>
                </div>
              </div>
            </div>
            <!-- <div ref="contentBottom"></div> -->
          </div>

          <div v-else-if="mainView === 'social'" class="cards-container">
            <div v-for="(tweet, i) in sidebarArticlesSocial" :key="i" class="card">
              <div style="width: 100%">
                <div class="main-body">
                  <div>
                    <div style="margin: 0 0 4px -2px" class="row">
                      <img
                        v-if="tweet.type === 'youtube'"
                        :src="youtubePlaceholder"
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <img
                        v-else-if="tweet.type === 'bluesky'"
                        :src="blueskyPlaceholder"
                        height="14px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <img
                        v-else-if="tweet.type === 'twitter'"
                        :src="twitterPlaceholder"
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />

                      <small v-if="tweet.type === 'twitter'">{{ tweet.user.username }}</small>
                      <small v-else> {{ tweet.author }}</small>
                    </div>

                    <p
                      v-if="tweet.type === 'twitter'"
                      @click="openTweet(tweet.user.username, tweet.id)"
                      style="cursor: pointer"
                      class="thin-span"
                    >
                      <span>{{ getTimeDifferenceInMinutes(tweet.created_at) }} </span>
                      -
                      {{ tweet.text }}
                    </p>

                    <p
                      class="thin-span"
                      v-else
                      @click="openTweetAlt(tweet.url)"
                      style="cursor: pointer"
                    >
                      <span>{{ getTimeDifferenceInMinutes(tweet.created_at) }} </span>
                      -
                      {{ tweet.title ? tweet.title : tweet.text }}
                    </p>
                    <!-- <div style="border-bottom: none; font-size: 14px; color: #484a6e" class="row">
                      <p class="thin-text">
                        {{ tweet.text }}
                      </p>
                    </div> -->
                  </div>

                  <div
                    v-if="tweet.type === 'twitter'"
                    @click="openTweet(tweet.user.username, tweet.id)"
                  >
                    <img :src="tweet.user.profile_image_url" class="card-photo-header" />
                  </div>

                  <div v-else @click="openTweetAlt(tweet.url)">
                    <img
                      v-if="tweet.type === 'youtube'"
                      :src="tweet.image_url"
                      class="card-photo-header"
                    />
                    <img
                      v-else
                      :src="tweet.image_url ? tweet.image_url : blueskyPlaceholder"
                      @error="onImageErrorAlt($event)"
                      class="card-photo-header"
                    />
                  </div>
                </div>
                <div class="row" style="margin: -4px 0 0 10px">
                  <p
                    v-if="tweet.type === 'twitter'"
                    @click="selectJournalist(tweet)"
                    class="turq-text"
                  >
                    @ <span>{{ tweet.user.username }}</span>
                  </p>

                  <p v-else class="turq-text" @click="selectJournalist(tweet)">
                    <span>{{ tweet.author }}</span>
                  </p>

                  <div
                    v-if="tweet.type === 'twitter'"
                    class="row"
                    style="margin-left: 12px; font-size: 12px"
                  >
                    <img src="@/assets/images/users.svg" height="11px" alt="" />
                    <p style="margin-left: 2px; font-size: 13px">
                      {{ formatNumber(tweet.user.public_metrics.followers_count) }}
                    </p>
                  </div>

                  <button
                    v-else
                    @click="analyzeVideo(tweet.id, tweet)"
                    style="margin-left: auto"
                    class="secondary-button alt-btn s-wrapper"
                    :disabled="isViewOnly"
                  >
                    <img
                      style="margin-right: 8px"
                      src="@/assets/images/sparkle.svg"
                      height="12px"
                      alt=""
                    />
                    Analyze

                    <div v-if="isViewOnly" class="s-tooltip">Locked</div>
                  </button>
                </div>
              </div>
            </div>
            <!-- <div ref="contentBottom"></div> -->
          </div>

          <div v-else-if="mainView === 'omni'" class="cards-container">
            <div v-for="(article, i) in sidebarArticlesOmni" :key="article.id" class="card">
              <div v-if="article.hasOwnProperty('snippet')" style="width: 100%">
                <div class="main-body">
                  <div>
                    <div style="margin: 0 0 4px -2px" class="row">
                      <img
                        :src="
                          article.source && article.source_img
                            ? article.source_img
                            : globePlaceholder
                        "
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <small>{{ article.source }}</small>
                    </div>

                    <p style="cursor: pointer" @click="goToArticle(article.link)">
                      {{ article.title }}
                    </p>
                    <div style="border-bottom: none; font-size: 14px; color: #484a6e" class="row">
                      <p class="thin-text">
                        {{ article.snippet }}
                      </p>
                    </div>
                  </div>

                  <div>
                    <img
                      @click="goToArticle(article.link)"
                      :src="article.image"
                      @error="onImageError($event)"
                      class="card-photo-header"
                    />
                  </div>
                </div>
                <div style="margin: -4px 0 0 10px">
                  <p @click="selectJournalist(article, true)" class="turq-text">
                    By <span>{{ article.author }}</span>
                  </p>
                </div>
              </div>

              <div v-else-if="article.hasOwnProperty('type')" style="width: 100%">
                <div class="main-body">
                  <div>
                    <div style="margin: 0 0 4px -2px" class="row">
                      <img
                        v-if="article.type === 'youtube'"
                        :src="youtubePlaceholder"
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <img
                        v-else-if="article.type === 'bluesky'"
                        :src="blueskyPlaceholder"
                        height="14px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <img
                        v-else-if="article.type === 'twitter'"
                        :src="twitterPlaceholder"
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />

                      <small v-if="article.type === 'twitter'">{{ article.user.username }}</small>
                      <small v-else> {{ article.author }}</small>
                    </div>

                    <p
                      v-if="article.type === 'twitter'"
                      @click="openTweet(article.user.username, article.id)"
                      style="cursor: pointer"
                      class="thin-span"
                    >
                      <span>{{ getTimeDifferenceInMinutes(article.created_at) }} </span>
                      -
                      {{ article.text }}
                    </p>

                    <p
                      class="thin-span"
                      v-else
                      @click="openTweetAlt(article.url)"
                      style="cursor: pointer"
                    >
                      <span>{{ getTimeDifferenceInMinutes(article.created_at) }} </span>
                      -
                      {{ article.title ? article.title : article.text }}
                    </p>
                    <!-- <div style="border-bottom: none; font-size: 14px; color: #484a6e" class="row">
                      <p class="thin-text">
                        {{ tweet.text }}
                      </p>
                    </div> -->
                  </div>

                  <div
                    v-if="article.type === 'twitter'"
                    @click="openTweet(article.user.username, article.id)"
                  >
                    <img :src="article.user.profile_image_url" class="card-photo-header" />
                  </div>

                  <div v-else @click="openTweetAlt(article.url)">
                    <img
                      v-if="article.type === 'youtube'"
                      :src="article.image_url"
                      class="card-photo-header"
                    />
                    <img
                      v-else
                      :src="article.image_url ? article.image_url : blueskyPlaceholder"
                      @error="onImageErrorAlt($event)"
                      class="card-photo-header"
                    />
                  </div>
                </div>
                <div class="row" style="margin: -4px 0 0 10px">
                  <p
                    v-if="article.type === 'twitter'"
                    @click="selectJournalist(article)"
                    class="turq-text"
                  >
                    @ <span>{{ article.user.username }}</span>
                  </p>

                  <p v-else class="turq-text" @click="selectJournalist(article)">
                    <span>{{ article.author }}</span>
                  </p>

                  <div
                    v-if="article.type === 'twitter'"
                    class="row"
                    style="margin-left: 12px; font-size: 12px"
                  >
                    <img src="@/assets/images/users.svg" height="11px" alt="" />
                    <p style="margin-left: 2px; font-size: 13px">
                      {{ formatNumber(article.user.public_metrics.followers_count) }}
                    </p>
                  </div>

                  <button
                    v-else
                    @click="analyzeVideo(article.id, article)"
                    style="margin-left: auto"
                    class="secondary-button alt-btn s-wrapper"
                    :disabled="isViewOnly"
                  >
                    <img
                      style="margin-right: 8px"
                      src="@/assets/images/sparkle.svg"
                      height="12px"
                      alt=""
                    />
                    Analyze

                    <div v-if="isViewOnly" class="s-tooltip">Locked</div>
                  </button>
                </div>
              </div>

              <div v-else style="width: 100%">
                <div class="main-body">
                  <div>
                    <div style="margin: 0 0 4px -2px" class="row">
                      <!-- src="@/assets/images/iconlogo.png" -->
                      <img
                        :src="
                          article.source && article.source.icon
                            ? article.source.icon
                            : globePlaceholder
                        "
                        height="12px"
                        alt=""
                        style="margin: 0 4px 0 1px"
                      />
                      <small>{{
                        mainView === 'trending'
                          ? article.source
                              .replace(/^https?:\/\//, '')
                              .replace(/^www\./, '')
                              .replace('.com', '')
                          : article.source.name
                      }}</small>
                    </div>

                    <p
                      style="cursor: pointer"
                      @click="goToArticle(mainView === 'trending' ? article.url : article.link)"
                    >
                      {{ article.title }}
                    </p>
                    <div style="border-bottom: none; font-size: 14px; color: #484a6e" class="row">
                      <p class="thin-text">
                        <span
                          >{{
                            getTimeDifferenceInMinutes(
                              mainView === 'trending' ? article.date : article.publish_date,
                            )
                          }}
                        </span>
                        -
                        {{ article.description }}
                      </p>
                    </div>
                  </div>

                  <div>
                    <img
                      @click="goToArticle(mainView === 'trending' ? article.url : article.link)"
                      :src="mainView === 'trending' ? article.image : article.image_url"
                      @error="onImageError($event)"
                      class="card-photo-header"
                    />
                  </div>
                </div>
                <div class="space-between" style="margin: -4px 0 0 10px">
                  <p @click="selectJournalist(article)" class="turq-text">
                    By <span>{{ extractJournalist(article.author) }}</span>
                  </p>

                  <button
                    @click="getTrafficData(article.url ? article.url : article.link, article)"
                    style="margin-right: 16px"
                    class="secondary-button alt-btn s-wrapper"
                    :disabled="isViewOnly"
                  >
                    <img
                      style="margin-right: 8px"
                      src="@/assets/images/sparkle.svg"
                      height="12px"
                      alt=""
                    />
                    Analyze

                    <div v-if="isViewOnly" class="s-tooltip">Locked</div>
                  </button>
                </div>
                <!-- <div v-if="articlesShowingDetails.includes(i)" style="margin: 8px" class="row">
                  <button
                    @click="selectJournalist(article)"
                    style="font-size: 10px; margin-right: 8px"
                    class="secondary-button-white"
                  >
                    Journalist Bio
                  </button>
                  <button
                    @click="getArticleSummary(article.link)"
                    style="font-size: 10px"
                    class="secondary-button-white"
                  >
                    Article Insights
                  </button>
                </div>

                <div
                  v-else
                  @click="toggleArticleActions(i)"
                  style="margin: 4px 0 0 8px; cursor: pointer; width: fit-content"
                >
                  <img
                    src="@/assets/images/more_horizontal.svg"
                    height="auto"
                    width="22px"
                    alt=""
                  />
                </div> -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Comms } from '@/services/comms'
import { quillEditor } from 'vue-quill-editor'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'
import AssistConversation from '../components/AssistConversation.vue'

export default {
  name: 'SearchSummaries',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    quillEditor,
    AssistConversation,
  },
  data() {
    return {
      searchingType: 'news',
      webIndexStart: 0,
      altWebIndexStart: 0,
      omniResults: [],
      omniNews: [],
      omniSocial: [],
      omniWeb: [],
      altOmniNews: [],
      altOmniSocial: [],
      altOmniWeb: [],
      threadCopy: {},
      selectedThread: null,
      followupShares: {},
      totalShares: {},
      editingProjects: false,
      selectedProject: null,
      projectId: '',
      shareUrl: '',
      currentThread: {},
      searchSaved: false,
      loadingAnalytics: false,
      showingAnalytics: false,
      currentArticle: {},
      noResultsString: 'No results found. Try a different request',
      alternateAricles: [],
      originalSearch: '',
      followUps: [],
      summaries: [],
      latestArticles: [],
      latestMedia: [],
      secondaryLoader: false,
      secondaryLoaderAlt: false,
      articlesShowingDetails: [],
      showingArticles: false,
      citationsMounted: true,
      altCitationsMounted: true,
      reportInstructions: '',
      urlsSet: false,
      urlPlaceholder: `
www.techcrunch.com/article-1 
www.bloomberg.com/article-2
www.forbes.com/article-3
     `,
      reportUrls: '',
      fileName: '',
      allowedFormats: ['image/jpeg', 'image/png', 'image/svg+xml'],
      maxSize: 2 * 1024 * 1024,
      loadingFile: false,
      showingBcc: false,
      showingCc: false,
      logoPlaceholder: require('@/assets/images/iconlogo.png'),
      journalistSvg: require('@/assets/images/profile.svg'),
      citationSvg: require('@/assets/images/info.svg'),
      globePlaceholder: require('@/assets/images/globe.svg'),
      twitterPlaceholder: require('@/assets/images/twitter-x.svg'),
      blueskyPlaceholder: require('@/assets/images/bluesky.png'),
      youtubePlaceholder: require('@/assets/images/youtube.png'),
      responseEmpty: false,
      bioModalOpen: false,
      contactsModalOpen: false,
      reportModalOpen: false,
      reportTitle: '',
      reportBrands: '',
      contactName: '',
      outletName: '',
      newContactBio: '',
      newContactImages: [],
      loadingContacts: false,
      showJournalistSuggestions: false,
      styleText: 'Select a writing style',
      uploadText: 'Great! Please provide a logo and banner file using JPEG, PNG, or SVG',
      coverageText: `Next, add news coverage links by pasting the URL's below.`,
      coverageInstructions: 'Last Step! Please provide overview instructions for this report.',
      lastInstructions: 'All set! We are now ready to run the report!',
      chatSearch: '',
      userResponse: null,
      secondResponse: null,
      thirdResponse: null,
      currentChat: null,
      chatting: false,
      showingDetailsEmail: false,
      showingStylesEmail: false,
      showingMainDetails: false,
      discoverList: [],
      drafting: false,
      originalSummary: null,
      placeholderTime: 'Select a time',
      alertType: 'EMAIL',
      alertChannel: '',
      alertChannelName: '',
      userChannelOpts: new SlackListResponse(),
      channelId: '',
      channelName: '',
      sendingSlack: false,
      searchTime: '',
      showingSave: false,
      showingShare: false,
      shareEmail: '',
      detailIndex: null,
      journalistIndex: null,
      showingName: false,
      hoverIndex: null,
      allCompanyDetails: [],
      detailTitle: '',
      detailsName: '',
      detailsBody: '',
      currentDetails: '',
      showingDetails: false,
      showingAllDetails: false,
      detailsInputModalOpen: false,
      pitchName: '',
      savedPitch: false,
      savedDiscovery: false,
      inputModalOpen: false,
      styleName: '',
      sample: '',
      savingStyle: false,
      journalistInfo: '',
      defaultWritingStyles: [
        {
          title: 'Default',
          style: `You are an AI PR assistant with the ability to create perfect, engaging content for any format. Your writing is modern, informal, and conversational—ideal for Millennial and Gen Z audiences. You excel at storytelling, using subtle persuasion without ever sounding salesy, and can adapt your tone and structure seamlessly to fit different content types.

To replicate the author's style, focus on the following guidelines:

Language: Relatable and conversational, never robotic or overly formal. Avoid jargon but maintain a polished feel.
Storytelling: Start with a strong hook, craft a compelling narrative, and conclude with an impactful ending.

Tone Adaptation: Adjust your style based on the content type:

Media Pitch: Short, under 150 words, breezy, intriguing, and tailored to the recipient. Open with Hi {journalist} followed by a relevant observation about the author and why this story is a fit for their readers.

Press Release: Professional yet warm and accessible. Emphasize key statistics and link them to industry trends. Use an attention-grabbing headline, crucial details early on, and compelling quotes. Aim for an engaging narrative that appeals to journalists.

Social Media Copy: Short, snappy, and aligned with trends.

Blog Post: Personal, insightful, and easy to digest.

Avoid Hard Sells: Focus on authenticity and building trust through storytelling rather than direct calls to action.

Persuasion: Use emotional and logical appeals subtly, guiding the reader naturally to a conclusion.

Your goal is to create content that resonates deeply, connects authentically, and compels action without being overt. Every word should feel like it was written by a human, unrecognizable by AI detectors.`,
        },
        // {
        //   title: 'Media Pitch',
        //   style: `
        // 1. Start email with "Hi {Journalist first name}", end with "Thanks,". Get right to it, no opening fluff like "I hope this message finds you well"
        // 2. Tone: Maintain a professional, respectful tone. Show appreciation for the journalist's work and express interest in collaboration.
        // 3. Formality: Use formal language, but avoid jargon. Keep sentences clear and concise.
        // 4. Structure: Start with a personalized greeting. Follow with a brief appreciation of the journalist's work, then introduce your topic. Provide key insights, then propose collaboration. End with a forward-looking statement and a thank you.
        // 5. Linguistic Idiosyncrasies: Use active voice and precise, impactful words. Include statistics and expert opinions for credibility.
        // 6. Credibility: Establish credibility by referencing recent research, expert opinions, and relevant industry trends.
        // 7. Engagement: Engage the reader by offering exclusive insights and proposing collaboration.
        // 8. Non-Promotional: Avoid promotional language. Focus on providing valuable, informative content.
        // 9. Stylistic Techniques: Use a mix of short and long sentences for rhythm. Use rhetorical questions to engage the reader and provoke thought.
        // `,
        // },
        // {
        //   title: 'Blog Post',
        //   style: `The author's style is formal and informative, using a journalistic tone to convey complex scientific concepts in a digestible manner. The structure is linear, starting with historical context and leading to the current developments. The author uses technical jargon, but also provides explanations to ensure understanding. Credibility is established through the mention of renowned scientists, historical achievements, and the university's long-standing involvement in the field. The author avoids persuasive language, focusing on facts and achievements.
        // Guidelines: Maintain a formal, journalistic tone. Use technical terms but provide explanations. Structure content linearly, starting with historical context. Establish credibility through mention of renowned figures and achievements. Avoid persuasive language, focusing on facts.`,
        // },
        // {
        //   title: 'Email',
        //   style: `1. Start with a friendly greeting: Use 'Hey' or 'Hi' to initiate a warm, approachable tone.
        // 2. Be direct and concise: Avoid fluff and unnecessary details. Get straight to the point.
        // 3. Maintain a neutral tone: Avoid persuasive or sales-oriented language. The tone should be informative, not promotional.
        // 4. Use simple, clear language: Avoid jargon or complex terms. The goal is to be understood by all readers.
        // 5. Structure: Use short sentences and paragraphs. Break up information into digestible chunks.
        // 6. Credibility: Use facts and data to support points. Avoid personal opinions or assumptions.
        // 7. Action point: End with a clear, actionable step for the reader. This should be direct and easy to understand.
        // 8. Informality: Maintain a casual, friendly tone throughout. This helps to engage the reader and make the content more relatable.
        // 9. Linguistic idiosyncrasies: Use common, everyday language. Avoid overly formal or academic language.
        // 10. Objectivity: Maintain an unbiased stance. Avoid taking sides or expressing personal views.`,
        // },
      ],
      personalStyles: true,
      writingStyle: '',
      writingStyleTitle: '',
      allWritingStyles: [],
      showingWritingStyles: false,
      showingStyles: false,
      showingDetails: false,
      showingAllDetails: false,
      showingHelp: false,
      supportEmail: 'support@mymanagr.com',
      showSuggestions: false,
      contentType: 'Content',
      showCompanySelection: false,
      showDateSelection: false,
      googleResults: [],
      relevantData: '',
      journalistData: '',
      listName: '',
      relatedTopics: [],
      loadingRelevant: false,
      loadingJournalists: false,
      journalisListtData: '',
      loadingRelated: false,
      showArrows: false,
      searchArticleText: '',
      searchTweetText: '',
      searchResultText: '',
      searchChannelText: '',
      showingChannels: false,
      showingAlertChannels: false,
      buttonClicked: false,
      savingContact: false,
      suggestions: [],
      loadingDraft: false,
      googleModalOpen: false,
      currentJournalistImages: [],
      currentJournalistBio: '',
      currentHeadline: '',
      currentDescription: '',
      currentDate: null,
      showingSources: false,
      currentJournalist: '',
      currentPublication: '',
      toolbarOptions: [
        ['bold', 'italic', 'underline', 'strike'], // toggled buttons
        ['link'],
        // next to link - 'image'
        [{ header: 1 }, { header: 2 }], // custom button values
        [{ list: 'ordered' }, { list: 'bullet' }, { list: 'check' }],

        [{ size: ['small', false, 'large', 'huge'] }], // custom dropdown

        ['clean'], // remove formatting button
      ],
      selectedOrg: '',
      bccEmail: '',
      ccEmail: '',
      targetEmail: '',
      revisedPitch: '',
      subject: 'subject',
      loadingPitch: false,
      sendingEmail: false,
      verifying: false,
      emailVerified: false,
      emailError: false,
      emailJournalistModalOpen: false,
      suggestionsLoading: false,
      currentIndex: 0,
      selectedFile: null,
      pdfLoaded: false,
      pdfLink: null,
      showSummaryMenu: false,
      expandedView: false,
      dateOpen: false,
      preparedTweets: null,
      addedClip: false,
      showSummaryInput: true,
      showSummaryInstructions: true,
      showingViews: false,
      summarizing: false,
      saveModalOpen: false,
      currentAlertId: null,
      alertSet: false,
      emailText: 'Activate Alerts',
      showNotifyBanner: false,
      currentAlert: null,
      emailAlerts: [],
      alertTIme: '',
      notifiedList: [],
      savingAlert: false,
      notifyModalOpen: false,
      formattedDate: '',
      dateStart: null,
      dateEnd: null,
      contentModalOpen: false,
      contentInstructions: null,
      contentUrl: null,
      showExpireModal: false,
      checkInterval: null,
      currentRow: null,
      addedArticles: [],
      clipLoading: false,
      uploadLink: null,
      success: true,
      articleBannerText: '',
      showArticleBanner: false,
      showArticleGenerateDropdown: false,
      optionIndex: null,
      contentLoading: false,
      addedClips: [],
      ShowReport: false,
      sentSummaryEmail: false,
      sendingSummaryEmail: false,
      sendSummaryEmailText: 'Email',
      showingPromptDropdown: false,
      sourceSummary: null,
      buttonText: 'Article Summary',
      AllUserTweets: {},
      mainView: 'omni',
      savedSearch: {},
      tweets: [],
      filteredArticles: [],
      trendingArticles: [],
      posts: [],
      tweetMedia: [],
      tweetUsers: null,
      articleInstructions: null,
      showArticleRegenerate: false,
      showSaveName: false,
      isTyping: false,
      searchName: null,
      searchId: null,
      threadId: null,
      textIndex: 0,
      typedMessage: '',
      tweetError: '',
      savingSearch: false,
      starterNum: 0,
      newSearch: '',
      newTemplate: '',
      additionalSources: '',
      outputInstructions: '',
      loading: false,
      summaryLoading: false,
      shouldCancel: false,
      regenModal: false,
      articles: [],
      summary: '',
      booleanString: null,
      metaData: { clips: [] },
      newSummary: false,
      addingPrompt: false,
      addingSources: false,
      loadingUrl: null,
      articleSummaryLoading: false,
      chatSummaryLoading: false,
      paidModal: false,
      showingDropdown: false,
      showGenerateDropdown: false,
      selectedOption: null,
      successModal: false,
      errorModal: false,
      selectedSearch: null,
      selectedDateTime: '',
      showingRelevant: false,
      showingJournalists: false,
      showingRelated: false,
      contentExamples: [
        {
          name: `Craft a press release...`,
          value: `Craft a press release for {Brand}`,
        },
        {
          name: `Help me brainstorm...`,
          value: `Help me brainstorm ideas for a ....`,
        },
        {
          name: `Write a social post...`,
          value: `Draft a LinkedIn post about {Topic}`,
        },
      ],
      omniExamples: [
        {
          name: `Latest news on..`,
          value: `Latest news on {Brand/Topic}`,
        },
        {
          name: ` Tell me about...`,
          value: `Tell me about {Journalist Name, Article Headline, URL, etc.}`,
        },
        {
          name: `Who's covering...`,
          value: `Who’s covering {Topic} ? List the 5 most influential, recognizable journalists.`,
        },
      ],
      newsExamples: [
        {
          name: `Top storylines...`,
          value: `Top storylines, influential journalists, and sentiment covering {Topic}`,
        },
        {
          name: `News roundup...`,
          value: `Provide a news roundup for {Brand}, include brand, competitors and industry updates`,
        },
        {
          name: `Who's writing about...`,
          value: `Who’s writing about {Topic} ? List the 5 most influential, recognizable journalists.`,
        },
      ],
      discoveryExamples: [
        {
          name: `U.S journalist covering...`,
          value: `U.S journalist covering {Topic}`,
        },
        {
          name: `Journalist similar to...`,
          value: `Journalist similar to...`,
        },
        {
          name: `Podcasters interested in...`,
          value: `Podcasters interested in {Topic}`,
        },
      ],
      socialExamples: [
        {
          name: `Top storylines about...`,
          value: `Top storylines about {Topic}`,
        },
        {
          name: `Analyze post about...`,
          value: `Analyze post about {Topic}`,
        },
        {
          name: `List top influencers covering...`,
          value: `List top influencers covering {Topic}`,
        },
      ],
      webExamples: [
        {
          name: ` Tell me about...`,
          value: `Tell me about {Journalist Name, Article Headline, URL, etc.}`,
        },
        {
          name: `Latest news on...`,
          value: `Latest news on {Topic, Brand, etc}`,
        },
        {
          name: `Who covered AI in 2024`,
          value: `Who covered AI in 2024`,
        },
      ],
      trendExamples: [
        {
          name: `What's trending in...`,
          value: `What's trending in {Industry} ?`,
        },
        {
          name: `Top headlines covering...`,
          value: `Show me top headlines covering {Topic}`,
        },
        {
          name: `Most shared stories..`,
          value: `List the 5 most shared stories`,
        },
      ],
      discoverExamples: [
        `Which US journalists would be interested in covering this story:`,
        `Podcaster that covers technology and AI`,
        `Frelancers that cover fashion`,
        `NY Times or WSJ writers covering climate change`,
      ],
      reportSuggestions: [
        `Summarize the coverage in paragraph form. Then provide sentiment analysis along with 3 key messages`,
        `List out the top 5 stories including outlet name, journalist, and date. Provide the articles impact on the brand`,
        `As the brands PR agency, provide a detailed analysis and the value of all the media overage we've secured.`,
      ],
      summarySuggestions: [
        `Craft a media pitch for [BrandX] incorporating relevant news, use citations. Pitch details: [here]`,
        `Craft a press release for [BrandX] incorporating relevant news, use citations. Pitch details: [here]`,
        `List up to 10 journalists that would be interested in writing about [BrandX], explain why`,
        `Provide creative pitching angles for [BrandX] based on this coverage`,
        `Provide sentiment analysis and key messages for [BrandX]`,
        `List 5 questions the media will ask [BrandX] based on this news`,
      ],
      searchExamples: [
        {
          title: 'Top storylines',
          text: 'Uncover top storylines about a popular topic or recent event',
          tag: `News`,
          tagClass: 'blue-bg',
          imgSource: require('@/assets/images/newspaper.svg'),
          view: 'news',
          chatText: 'Scan the news and list top storylines',
          chatResponse: 'Using the message bar, enter a topic, industry, or company',
          searchText:
            'List the top 5 storylines based on the provided news coverage. Always Use Labels. Always Use citations.',
          details: false,
        },
        {
          title: 'Active reporters',
          text: 'Find journalists actively covering a news topic or event for your brand',
          tag: `News`,
          tagClass: 'blue-bg',
          imgSource: require('@/assets/images/megaphone.svg'),
          view: 'news',
          chatText: 'Find journalists actively covering a news topic that I can pitch',
          chatResponse:
            "Using Company details, provide a short description of your company or a pitch you're working on",
          searchText: `List the journalists from recognizable news outlets (up to 10). Only list journalist from the news coverage.
          Then suggest which of these journalists the company listed should pitch and why. The list must be returned in an html unordered list. Always use Labels. Always use citations.
          Company:`,
          details: true,
          responseText: 'Using the message bar, provide a current news topic or event',
        },
        {
          title: 'Media list',
          text: 'Get a list of journalists based on the content of your pitch',
          tag: `Discover`,
          tagClass: 'turq-bg',
          imgSource: require('@/assets/images/target.svg'),
          view: 'discover',
          chatText: 'Find relevant journalists',
          chatResponse: 'What type of journalists are you looking for ?',
          details: false,
        },
        {
          title: 'Find a journalist',
          text: 'Lookup a journalist by name and get a real-time bio',
          tag: `Network`,
          tagClass: 'orange-bg',
          imgSource: require('@/assets/images/glasses.svg'),
          view: 'network',
          chatText: 'Uncover top storylines',
          chatResponse: 'Using the message bar, enter a topic, industry, or company',
        },
        {
          title: 'Competitor update',
          text: `Stay up to speed on what the competition is doing`,
          tag: `News`,
          tagClass: 'blue-bg',
          imgSource: require('@/assets/images/sparkles-nofill-round.svg'),
          view: 'news',
          chatText: 'What are my competitors up to and how does it impact my brand?',
          chatResponse: `Using Company details, provide your brand's name`,
          searchText: `Based on the news coverage, provide a competitor update to the following company's PR team. Break it down into sections per competitor, provide sentiment analysis, top 3-5 take aways, and a super creative, targeted PR campaign suggestion for the company's PR team based on competitor coverage. Always Use Labels and break into multiple sections. Always Use citations. Company details here:`,
          details: true,
          responseText:
            'Using the message bar below, provide up to 3 competitors using OR in between',
        },
        {
          title: 'Media Q&A',
          text: 'See which questions the media may ask based on recent news events',
          tag: `News`,
          tagClass: 'blue-bg',
          imgSource: require('@/assets/images/microphone-alt.svg'),
          view: 'news',
          chatText: 'Questions the media may ask based on recent news',
          chatResponse: 'First, tell us about your company (e.g., name and short description)',
          searchText:
            'Based on the news coverage, list 5 questions the media will ask this company. Provide suggested answers as well. Always Use Labels. Always Use citations. :',
          details: true,
          responseText: 'Using the message bar, provide a current news topic or event',
        },
        {
          title: 'Writing assistant',
          text: 'Craft a media pitch, press release, or social post that sounds like you',
          tag: `Write`,
          tagClass: 'pink-bg',
          imgSource: require('@/assets/images/edit-note.svg'),
          view: 'write',
          chatText: 'Generate content for me',
          chatResponse: 'First, tell us about your company (e.g., name and short description)',
          details: true,
          responseText: 'Great! What would you like me to write for you ?',
        },
        {
          title: 'Web searching',
          text: 'Get questions answered based on top ranking web data',
          tag: `Web`,
          tagClass: 'purp-bg',
          imgSource: require('@/assets/images/google.svg'),
          view: 'web',
          chatText: 'Web searching',
          chatResponse: 'What would you like to know ?',
          details: false,
        },
        // {
        //   title: 'Coverage report',
        //   text: 'Create an earned media report for your brand',
        //   tag: `Report`,
        //   tagClass: 'purp-bg',
        //   imgSource: require('@/assets/images/report.svg'),
        //   view: 'report',
        //   chatText: 'Help me create a coverage report',
        //   chatResponse: 'Using the message bar, tell us which brand this report is for',
        //   details: false,
        // },
      ],
      socialSearchExamples: [`Top fashion trends`, `Why is Taylor Swift trending`, `from: nytimes`],
      googleSearchExamples: [
        `Emerging fashion journalists`,
        `List top travel destinations in 2024`,
        `Who is NYT journalist David Brooks`,
      ],
      testExamples: [
        'How is sustainable fashion evolving in 2024',
        'How is sustainable fashion evolving in 2024',
        'How is sustainable fashion evolving in 2024',
      ],

      summaryExamples: [
        {
          name: `Topic Summary`,
          value: `Summarize the news about {TopicX} (in paragraph form, multiple short paragraphs for optimal readability). Focus on key research, advancements, regulatory changes, industry trends, and professional development. Focus only on US stories and disregard stock related news. `,
        },
        {
          name: 'Audience Analysis',
          value: `Summarize the news about {TopicX} (in paragraph form, multiple short paragraphs for optimal readability). Identify what aspects of the topic are most intriguing or concerning to the public. Focus only on US stories and disregard stock related news.`,
        },
        {
          name: `List Journalists`,
          value: `List 5 journalists (from top pubs, what they wrote, and include pitching tips) I can pitch on behalf of {BrandX}`,
        },
        {
          name: `Create Press Release`,
          value: `Generate a press release for {BrandX} based on recent news on {TopicX}. Extract key trends and stats, link activities to the news, and include an expert quote. Ensure the content aligns with the mission for maximum engagement. `,
        },
        {
          name: `Enhance Press Release`,
          value: `Update the provided press release by integrating relevant, recent news to make it more timely and contextual. Focus on connecting the company's announcements with current industry trends, significant events, and the latest data and statistics. Ensure the updated release reflects the company's proactive role in the industry. Flag the new content. Here the release: {PressReleaseSnippet}`,
        },
        {
          name: `Enhance Media Pitch`,
          value: `Update the provided media pitch by integrating relevant, recent news to make it more timely and contextual. Focus on connecting the company's announcements with current industry trends, significant events, and the latest data and statistics. Ensure the updated pitch reflects the company's proactive role in the industry. Flag the new content. Here the release: {MediaPitch}`,
        },
        {
          name: `Newsjacking Ideas`,
          value: `Provide creative newsjacking ideas for {BrandX} based on this coverage`,
        },
        {
          name: `Media Q&A`,
          value: `List 5 questions & answers journalists would ask {BrandX} leadership team`,
        },
        {
          name: `Expert Q&A`,
          value: `Generate a list of 5 questions that the public might have about this topic and how an expert {ExpertX} would respond to them.`,
        },
        {
          name: `Pitch Expert`,
          value: `Bring {BrandX} up to speed on what’s happening in terms of {TopicX}. Identify what aspects of the topic are most intriguing or concerning to the public. Identify which of their industry expects could be pitched to the media. No salutations.`,
        },
        {
          name: `Brand Analysis`,
          value: `Summarize the news about {BrandX} (in paragraph form) - keep in mind, all these clips mention them in the article. Identify what aspects of the topic are most intriguing or concerning to the public. Then (separate paragraph), flag the top 3 stories (headline, source, author, and date mm/dd). End with a short line on overall brand sentiment.`,
        },
        {
          name: `Crisis Comms`,
          value: `IF there is a negative story about {BrandX} or a potential crisis is brewing, then flag the story (headline, source, author, date using mm/dd format) and draft a short crisis communication statement, and suggest 2-3 key messages for damage control. If there is crisis, simply reply with {All good, no crisis :)}`,
        },
        {
          name: `Competitor Update`,
          value: `Bring {BrandX} up to speed on what {CompetitorX} is up to and why it matters, in paragraph form. Only flag the most impactful stories.  One short paragraph for positive and another for negative stories (headline, source, author, date in mm/dd format). Lastly offer 2-3 super creative newsjacking ideas.`,
        },
        {
          name: `Issue Statement`,
          value: `Issue a statement on behalf of {BrandX}`,
        },
        {
          name: `Blog Post`,
          value: `Draft an informative blog post based on this coverage for {BrandX}`,
        },
        {
          name: `SEO Suggestions`,
          value: `Provide top 10 SEO suggestions relating to this topic for {BrandX}`,
        },
        // {
        //   name: `Sales Meeting`,
        //   value: `I am a sales rep, you are the VP of Sales, bring me up to speed on whats happening in the industry and how I can leverage it to sell my product: {ProductX} -- provide super specific, tangible, and creative advice.`,
        // },
        // {
        //   name: `Email Roundup`,
        //   value: `Craft an email roundup for {BrandX} leadership team bringing them up to speed on the most important, relevant, impactful news. Offer advice at the end. Be short, direct, to the point. No fluff.`,
        // },
      ],
      articleGenerateOptions: [
        { name: 'Press Release', value: `Press Release` },
        { name: 'Statement', value: 'Statement' },
        { name: `Media Pitch`, value: `Media Pitch` },
        { name: `Blog Post`, value: `Blog Post` },
        { name: `LinkedIn Post`, value: `LinkedIn Post` },
        { name: `Twitter Post`, value: `Twitter Post` },
        { name: 'Email', value: 'Email' },
        { name: 'Other', value: '' },
      ],
      generateOptions: [
        { name: 'Basic summary', value: 'Summarize the news' },
        {
          name: 'Advanced summary',
          value: `Summarize the news for XXX, provide sentiment, creative ways they can newsjack this coverage, and list 5 journalists from Tier 1 publications that will write about this, along with creative pitching tips`,
        },
        {
          name: 'PR agency',
          value:
            'As XXX PR agency, provide an update on what the competition is doing along with super creative ways to newsjack this coverage',
        },
        {
          name: `List top headlines`,
          value: `List 5 of the most important headlines ( include source name + journalist) and the impact on XXX`,
        },
        {
          name: `List 10 journalists`,
          value: `List 10 journalists from Tier 1 publications and creative tips to pitch them`,
        },
        {
          name: `Media report`,
          value: `Create a media monitoring report for XXX. Include top sources (based on popularity and size), number of articles, sentiment, and any other important metrics`,
        },
        {
          name: 'Address negative coverage',
          value: 'Respond to all the negative coverage on behalf of XXX',
        },
        {
          name: 'Q & A',
          value: 'Generate 5 questions & answers journalists would ask based on this news',
        },
        {
          name: 'Write media pitch',
          value: 'Create a media pitch on behalf of XXX based on this coverage',
        },
        {
          name: 'Write blog post',
          value: 'Write a highly engaging blog post based on this coverage for XXX',
        },
        {
          name: 'Issue statement',
          value: 'Issue a statement on behalf of XXX based on this covarage',
        },
      ],
      upgradeMessage: 'You have reached your usage limit for the month. Please upgrade your plan.',
      copyTip: 'Copy',
      copyShareTip: 'Copy Link',
      searchSuggestions: [
        `What is the PR impact of this coverage`,
        `Find me the most positive / negative article`,
        'Analyze the media to identify what aspects of the topic are most intriguing or concerning to the public.',
        `Generate a list of 5 questions that the public might have about this topic and how an expert in the field would respond to them.`,
        `Provide top 10 SEO phrases relating to this topic`,
        `Provide creative newsjacking ideas for XXX based on this coverage`,
        `Provide new pitching angles for XXX based on this news`,
        `Provide a comprehensive media monitoring insight dashboard (list top sources, estimate the potential reach, sentiment analysis, competitor highlights, etc.)`,
        `List 5 of the most important headlines (include source name + journalist)`,
        `List 5 journalists (from top pubs, include pitching tips) I can pitch on behalf of XXX`,
        `List 5 questions & answers journalists would ask about XXX`,
        `Issue a statement on behalf of XXX`,
        `Write a blog post based on this coverage`,
      ],
      promptSuggestions: [
        `"Coca-Cola"`,
        `"Commercial real estate" AND "Technology"`,
        `"OpenAI" OR "Google Bard"`,
        `"Apple no stock related news"`,
      ],
      pitchStyle: `You are an AI PR assistant with the ability to create perfect, engaging content for any format. Your writing is modern, informal, and conversational—ideal for Millennial and Gen Z audiences. You excel at storytelling, using subtle persuasion without ever sounding salesy, and can adapt your tone and structure seamlessly to fit different content types.

      To replicate the author's style, focus on the following guidelines:

      Language: Relatable and conversational, never robotic or overly formal. Avoid jargon but maintain a polished feel.
      Storytelling: Start with a strong hook, craft a compelling narrative, and conclude with an impactful ending.

      Tone Adaptation: Adjust your style based on the content type:

      Media Pitch: Short, under 150 words, breezy, intriguing, and tailored to the recipient. Open with Hi {journalist} followed by a relevant observation about the author and why this story is a fit for their readers.

      Press Release: Professional yet warm and accessible. Emphasize key statistics and link them to industry trends. Use an attention-grabbing headline, crucial details early on, and compelling quotes. Aim for an engaging narrative that appeals to journalists.

      Social Media Copy: Short, snappy, and aligned with trends.

      Blog Post: Personal, insightful, and easy to digest.

      Avoid Hard Sells: Focus on authenticity and building trust through storytelling rather than direct calls to action.

      Persuasion: Use emotional and logical appeals subtly, guiding the reader naturally to a conclusion.

      Your goal is to create content that resonates deeply, connects authentically, and compels action without being overt. Every word should feel like it was written by a human, unrecognizable by AI detectors.`,
      dropdownLoading: false,
      traffic: null,
      socialData: null,
    }
  },
  created() {
    this.shouldCancel = false

    if (this.$route.query && this.$route.query.success) {
      if (this.$route.query.success === 'true') {
        this.successModal = true
      } else {
        this.errorModal = true
      }
    }

    const today = new Date()
    const sevenDaysAgo = new Date(today)
    sevenDaysAgo.setDate(today.getDate() - 7)

    this.dateStart = sevenDaysAgo.toISOString().split('T')[0]
    this.dateEnd = today.toISOString().split('T')[0]

    const defaultTime = new Date()
    defaultTime.setHours(8, 0)
    this.selectedTime = defaultTime.toISOString().slice(0, 16)

    this.$store.dispatch('updateListName', 'news')

    if (!this.$route.params.code) {
      this.getWritingStyles()
      this.getCompanyDetails()
      this.shareEmail = this.user.email

      if (this.user.slackRef) {
        this.listUserChannels()
      }
    }
  },
  watch: {
    typedMessage: 'changeIndex',
    currentSearch(newVal, oldVal) {
      if (newVal && newVal.id !== (oldVal ? oldVal.id : null)) {
        this.setSearch(newVal)
      }
    },
    emailJournalistModalOpen(newVal, oldVal) {
      if (newVal === true) {
        this.emailVerified = false
        this.emailError = false
        this.revisedPitch = ''
        this.targetEmail = ''
        this.subject = 'subject'
        this.ccEmail = ''
        this.bccEmail = ''
      }
    },
    targetEmail(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.emailVerified = false
        this.emailError = false
      }
    },
    googleModalOpen(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.buttonClicked = false
      }
    },
    mainView(newVal, oldVal) {
      if (newVal !== oldVal) {
        if (newVal === 'write') {
          this.writeSetup()
        } else {
          this.writeSetup()
        }
      }
    },
  },
  updated() {
    if (!this.citationsMounted) {
      this.setTooltips()

      const journalistElements = document.querySelectorAll('.select-journalist')

      if (this.mainView === 'news' || this.mainView === 'trending') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            try {
              const citation = this.filteredArticles[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Error:', error)
            }
          })
        })
      } else if (this.mainView === 'web') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            try {
              const citation = this.googleResults[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      } else if (this.mainView === 'social') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            try {
              const citation = this.tweets[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      } else if (this.mainView === 'omni') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            try {
              const citation = this.omniResults[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      }
    }

    if (!this.altCitationsMounted) {
      this.setTooltipsAlt()

      const journalistElements = document.querySelectorAll('.select-journalist-alt')

      if (this.mainView === 'news' || this.mainView === 'trending') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            const summaryIndex = event.target.getAttribute('summary-index')

            try {
              const citation =
                this.summaries[summaryIndex] && this.summaries[summaryIndex].clips.length
                  ? this.summaries[summaryIndex].clips[citationIndex]
                  : this.filteredArticles[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      } else if (this.mainView === 'web') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            const summaryIndex = event.target.getAttribute('summary-index')

            try {
              const citation =
                this.summaries[summaryIndex] && this.summaries[summaryIndex].clips.length
                  ? this.summaries[summaryIndex].clips[citationIndex]
                  : this.googleResults[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      } else if (this.mainView === 'social') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            const summaryIndex = event.target.getAttribute('summary-index')

            try {
              const citation =
                this.summaries[summaryIndex] && this.summaries[summaryIndex].clips.length
                  ? this.summaries[summaryIndex].clips[citationIndex]
                  : this.tweets[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      } else if (this.mainView === 'omni') {
        journalistElements.forEach((element) => {
          element.addEventListener('click', (event) => {
            const citationIndex = event.target.getAttribute('data-citation')
            const summaryIndex = event.target.getAttribute('summary-index')

            try {
              const citation =
                this.summaries[summaryIndex] && this.summaries[summaryIndex].clips.length
                  ? this.summaries[summaryIndex].clips[citationIndex]
                  : this.omniResults[citationIndex]
              this.selectJournalist(citation)
            } catch (error) {
              console.error('Failed to parse citation JSON:', error)
              console.error('Error:', error)
            }
          })
        })
      }
    }
  },
  mounted() {
    if (!this.$route.params.code) {
      this.getEmailAlerts()
      this.pitchStyleSetup()
      this.setPlaceholder()
    }

    const path = this.$route.path.replace(/\/$/, '') // Remove trailing slash
    const matches = path.match(/\/summaries\/(.+)/)
    if (matches && matches[1]) {
      const code = matches[1]
      this.shareThread(code)
    }
  },
  beforeDestroy() {
    this.abortFunctions()
  },
  methods: {
    async addLinkInteraction(url) {
      try {
        const res = await User.api.addInteraction({
          type: 'link',
          article_link: url,
        })
      } catch (e) {
        console.log(e)
      }
    },
    goToReports() {
      let data = {}

      if (this.savedSearch) {
        data.thread = this.savedSearch
      } else {
        data.thread = this.threadCopy
      }

      data.title = this.reportTitle
      data.brand = this.reportBrands

      this.$store.dispatch('updateSharedObject', data)
      this.$router.push({ name: 'Reports' })
    },
    openReportModal() {
      if (this.searchSaved && this.reportCredits > 0) {
        this.reportModalOpen = true
      }
    },
    async shareThread(code) {
      try {
        const res = await Comms.api.shareThread({
          code: code,
        })
        this.setSearch(res.data)
        this.$store.dispatch('updateViewOnly', true)
      } catch (e) {
        console.log(e)
        this.$toast('Thread does not exist', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async saveThread() {
      this.savingSearch = true
      try {
        const res = await Comms.api.saveThread({
          user: this.user.id,
          title: this.searchName,
          meta_data: {
            searchTerm: this.newSearch,
            summary: this.summary,
            list: this.discoverList,
            articlesFiltered: this.articlesFiltered,
            filteredResults: this.filteredResults,
            tweetMedia: this.tweetMedia,
            summaries: this.summaries,
            followUps: this.followUps,
            preparedTweets: this.preparedTweets,
            googleResults: this.googleResults,
            filteredArticles: this.filteredArticles,
            type: this.mainView,
            originalSearch: this.originalSearch,
            tweets: this.tweets,
            followupShares: this.followupShares,
            totalShares: this.totalShares,
            boolean: this.booleanString,
            project: this.selectedOrg,
            omniNews: this.omniNews,
            omniResults: this.omniResults,
            omniSocial: this.omniSocial,
            omniWeb: this.omniWeb,
            altOmniNews: this.altOmniNews,
            altOmniSocial: this.altOmniSocial,
            altOmniWeb: this.altOmniWeb,
          },
        })

        this.threadCopy = {
          user: this.user.id,
          title: this.searchName,
          meta_data: {
            searchTerm: this.newSearch,
            summary: this.summary,
            list: this.discoverList,
            articlesFiltered: this.articlesFiltered,
            filteredResults: this.filteredResults,
            tweetMedia: this.tweetMedia,
            summaries: this.summaries,
            followUps: this.followUps,
            preparedTweets: this.preparedTweets,
            googleResults: this.googleResults,
            filteredArticles: this.filteredArticles,
            type: this.mainView,
            originalSearch: this.originalSearch,
            tweets: this.tweets,
            followupShares: this.followupShares,
            totalShares: this.totalShares,
            boolean: this.booleanString,
            project: this.selectedOrg,
            omniNews: this.omniNews,
            omniResults: this.omniResults,
            omniSocial: this.omniSocial,
            omniWeb: this.omniWeb,
            altOmniNews: this.altOmniNews,
            altOmniSocial: this.altOmniSocial,
            altOmniWeb: this.altOmniWeb,
          },
        }
        this.savedSearch = res
        this.threadId = res.id
        // this.showingSave = false
        this.savingSearch = false
        this.$toast('Thread Saved', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })

        if (this.mainView !== 'news' && this.mainView !== 'social') {
          this.hideSave()
        }

        this.searchSaved = true
        this.refreshUser()
        this.$store.dispatch('getThreads')
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    removeDomain(url) {
      if (url) {
        const domainRegex = /\.(com|net|org|gov|edu|co|io|biz|info|us)$/i

        return url.replace(domainRegex, '')
      } else {
        return 'Unknown'
      }
    },
    async analyzeVideo(id, tweet) {
      this.loadingAnalytics = true
      this.showingAnalytics = true
      this.currentArticle = tweet

      try {
        if (tweet.type === 'bluesky') {
          const res = await Comms.api.getBlueskyProfile({
            id: id,
          })

          this.currentArticle.traffic = res
        } else {
          const res = await Comms.api.analyzeVideo({
            video_id: id,
          })

          this.currentArticle.traffic = res
        }

        this.loadingAnalytics = false
      } catch (e) {
        console.log(e)
      }
    },
    async getTrafficData(url, article) {
      this.loadingAnalytics = true
      this.showingAnalytics = true

      this.currentArticle = article
      try {
        const res = await Comms.api.getTrafficData({
          urls: [url],
        })
        this.traffic = res
        this.getSocialData(url)
      } catch (e) {
        console.error(e)
        this.loading = false
        // this.$toast('Error uploading clips, try again', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      }
    },
    async getSocialData(url) {
      try {
        const res = await Comms.api.getSocialData({
          urls: [url],
        })
        this.socialData = res
        this.combineArticleWithTraffic()
      } catch (e) {
        console.error(e)
        this.loadingAnalytics = false
      }
    },

    combineArticleWithTraffic() {
      // const domain = this.currentArticle.link
      //   .replace(/^https?:\/\//, '')
      //   .replace(/^www\./, '')
      //   .split('/')[0]

      const traffic = Object.values(this.traffic)[0] || {}
      const social = Object.values(this.socialData)[0] || {}

      this.currentArticle = {
        ...this.currentArticle,
        traffic,
        social,
      }

      this.getArticleSummary(
        this.currentArticle.link ? this.currentArticle.link : this.currentArticle.url,
      )
    },

    async getArticleSummary(url, instructions = null) {
      try {
        const response = await Comms.api.getArticleSummary({
          url: url,
          search: this.booleanString,
          instructions: instructions,
        })

        if (this.shouldCancel) {
          return this.stopLoading()
        }

        this.currentArticle['summary'] = response.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')

        this.loadingAnalytics = false
        this.refreshUser()
        console.log('CURRENT ARTICLE --- > ', this.currentArticle)
      } catch (e) {
        console.log(e)
        this.$toast('Article analysis not available', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })

        this.loadingAnalytics = false
      } finally {
        // this.showArticleRegenerate = false
        // this.loadingUrl = null
      }
    },

    formatNumberAlt(number) {
      if (number === '0' || number === 0 || !number) {
        return 0
      }

      const roundedNumber = Math.ceil(number)

      return roundedNumber.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },

    setOriginalArticles() {
      this.alternateAricles = []
      this.showingArticles = true
    },
    setAndShowArticles(clips) {
      this.alternateAricles = clips
      this.showingArticles = true
    },
    toggleArticleActions(i) {
      this.articlesShowingDetails.push(i)
    },
    setTooltipsAlt() {
      const citationWrappers = document.querySelectorAll('.citation-wrapper-alt')
      if (citationWrappers.length === 0) {
        return
      } else {
        // this.altCitationsMounted = true
      }

      citationWrappers.forEach((wrapper) => {
        let hideTimeout
        const tooltip = wrapper.querySelector('.citation-tooltip')

        if (!tooltip) {
          return
        }

        // Show tooltip when hovering over the wrapper
        wrapper.addEventListener('mouseenter', () => {
          clearTimeout(hideTimeout)
          tooltip.classList.add('show')
        })

        // Hide tooltip after a delay when leaving the wrapper and tooltip
        wrapper.addEventListener('mouseleave', () => {
          hideTimeout = setTimeout(() => {
            tooltip.classList.remove('show')
          }, 300)
        })

        // Ensure tooltip stays visible when hovering over the tooltip itself
        tooltip.addEventListener('mouseenter', () => {
          clearTimeout(hideTimeout)
        })

        // Hide tooltip after a delay when leaving the tooltip
        tooltip.addEventListener('mouseleave', () => {
          hideTimeout = setTimeout(() => {
            tooltip.classList.remove('show')
          }, 300)
        })
      })
    },

    setTooltips() {
      const citationWrappers = document.querySelectorAll('.citation-wrapper')
      if (citationWrappers.length === 0) {
        return
      } else {
        this.citationsMounted = true
      }

      citationWrappers.forEach((wrapper) => {
        let hideTimeout
        const tooltip = wrapper.querySelector('.citation-tooltip')

        if (!tooltip) {
          return
        }

        // Show tooltip when hovering over the wrapper
        wrapper.addEventListener('mouseenter', () => {
          clearTimeout(hideTimeout)
          tooltip.classList.add('show')
        })

        // Hide tooltip after a delay when leaving the wrapper and tooltip
        wrapper.addEventListener('mouseleave', () => {
          hideTimeout = setTimeout(() => {
            tooltip.classList.remove('show')
          }, 300)
        })

        // Ensure tooltip stays visible when hovering over the tooltip itself
        tooltip.addEventListener('mouseenter', () => {
          clearTimeout(hideTimeout)
        })

        // Hide tooltip after a delay when leaving the tooltip
        tooltip.addEventListener('mouseleave', () => {
          hideTimeout = setTimeout(() => {
            tooltip.classList.remove('show')
          }, 300)
        })
      })
    },
    setUrls() {
      this.urlsSet = true
      this.scrollToChatTop()
    },
    uploadImage(event) {
      const file = event.target.files[0]

      if (!file) {
        this.fileName = ''
        alert('No file selected.')
        return
      }

      if (!this.allowedFormats.includes(file.type)) {
        alert('Only JPEG, PNG, and SVG files are allowed.')
        this.fileName = ''
        return
      }

      if (file.size > this.maxSize) {
        alert('File size should not exceed 2MB.')
        this.fileName = ''
        return
      }

      this.loadingFile = true
      this.fileName = file.name
      this.scrollToChatTop()

      const reader = new FileReader()

      reader.onload = (e) => {
        const imageDataUrl = e.target.result
        // may start displaying the image
        console.log('Uploaded Image:', imageDataUrl)
        // Will send imageDataUrl to the server here
        this.loadingFile = false
      }

      reader.onerror = () => {
        alert('Error reading file.')
        this.fileName = ''
        this.loadingFile = false
      }

      reader.readAsDataURL(file)
    },
    onImageErrorAlt(event) {
      event.target.src = this.blueskyPlaceholder
    },
    onImageError(event) {
      event.target.src = this.logoPlaceholder
    },
    toggleBioModal() {
      this.bioModalOpen = !this.bioModalOpen
    },
    toggleContactsModal() {
      this.hideSources()
      this.contactsModalOpen = !this.contactsModalOpen
    },
    hideJournalistSuggestions() {
      this.showJournalistSuggestions = false
    },
    toggleJournalistSuggestions() {
      this.showJournalistSuggestions = true
      this.scrollToChatTop()
    },
    setChatSuggestion(val) {
      this.chatSearch = val
    },
    selectAlertChannel(channel) {
      this.alertChannelName = channel.name
      this.alertChannel = channel.id
      this.hideAlertChannels()
    },
    selectChannel(channel) {
      this.channelName = channel.name
      this.channelId = channel.id
      this.hideChannels()
    },
    showAlertChannels() {
      this.showingAlertChannels = true
    },
    hideAlertChannels() {
      this.showingAlertChannels = false
      this.searchChannelText = ''
    },
    showChannels() {
      this.showingChannels = true
    },
    hideChannels() {
      this.showingChannels = false
      this.searchChannelText = ''
    },
    clearPlaceholder() {
      this.placeholderTime = ''
    },
    setPlaceholder() {
      if (!this.alertTIme) {
        this.placeholderTime = 'Select a time'
      }
    },
    toggleAlert(type) {
      if (this.alertType === type) {
        this.alertType = null
      } else {
        this.alertType = type
      }
    },
    async listUserChannels(cursor = null) {
      this.dropdownLoading = true
      try {
        const res = await SlackOAuth.api.listUserChannels(cursor)
        const results = new SlackListResponse({
          channels: [...this.userChannelOpts.channels, ...res.channels],
          responseMetadata: { nextCursor: res.nextCursor },
        })
        this.userChannelOpts = results
      } catch (e) {
        console.log(e)
      } finally {
        this.dropdownLoading = false
      }
    },
    showSave() {
      this.showingSave = true
    },
    hideSave() {
      this.showingSave = false
    },
    showShare() {
      this.showingShare = true
    },
    hideShare() {
      this.showingShare = false
    },
    async deleteWritingStyle(id) {
      try {
        await Comms.api.deleteWritingStyle({ style_id: id })
        this.$toast('Writing Style removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.writeSetup()
        this.getWritingStyles()
        this.refreshUser()
      }
    },
    selectProject(project) {
      console.log('here', project)
      this.selectedProject = project
      this.editingProjects = true
      console.log(this.selectedProject)
    },
    async deleteCompanyDetails(id) {
      try {
        const res = await Comms.api.deleteCompanyDetails({
          id: id,
        })
        this.$toast('Project removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.detailTitle = ''
        this.currentDetails = ''
        this.selectedOrg = ''
        this.getCompanyDetails()
        this.refreshUser()
        this.editingProjects = false
        this.selectedProject = null
      }
    },

    async updateProject() {
      try {
        const res = await Comms.api.updateCompanyDetails({
          id: this.selectedProject.id,
          details: this.selectedProject.details,
        })
        this.$toast('Project updated', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.addDetails(this.selectedProject.title, this.selectedProject.details)
        this.selectedProject = null
      } catch (e) {
        console.log(e)
      } finally {
        this.getCompanyDetails()
        this.refreshUser()
        this.editingProjects = false
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
    async addCompanyDetails() {
      this.savingStyle = true
      try {
        const res = await Comms.api.addCompanyDetails({
          user: this.user.id,
          title: this.detailsName,
          details: this.detailsBody,
        })
        this.$toast('Details saved', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.refreshUser()
      } catch (e) {
        console.log(e)
      } finally {
        this.detailsName = ''
        this.detailsBody = ''
        // this.getDetails()
        this.savingStyle = false
        this.getCompanyDetails(true)
        this.toggleDetailsInputModal()
      }
    },
    async sendToSlack() {
      this.sendingSlack = true
      try {
        const res = await SlackOAuth.api.sendToSlack({
          search: this.newSearch,
          start_date: this.dateStart,
          end_date: this.dateEnd,
          summary: this.originalSummary,
          channel_id: this.channelId,
          clips:
            this.mainView === 'news'
              ? this.articlesFiltered.slice(0, 5)
              : this.filteredTweets.slice(0, 5),
        })
        this.$toast('Sent to Slack', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        console.log(res)
      } catch (e) {
        if (e.data.error) {
          this.$toast(`${e.data.error}`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Error sending content, try again later', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        this.sendingSlack = false
        this.hideShare()
      }
    },
    clearList() {
      this.journalisListtData = ''
      this.journalistInfo = ''
      // this.showingJournalistsList = false
    },
    async getDiscoveries() {
      this.$store.dispatch('getDiscoveries')
    },
    async discoverJournalists(discover = false) {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }

      if (discover) {
        this.loading = true

        this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      }

      if (this.savedDiscovery) {
        this.savedDiscovery = false
      }

      try {
        const res = await Comms.api.discoverJournalists({
          info: discover ? this.newSearch : this.followUps[this.followUps.length - 1],
          content: '',
          discover: discover,
          previous: this.summaries.length
            ? this.summaries[this.summaries.length - 1].list
            : this.discoverList
            ? this.discoverList
            : '',
        })

        if (this.searchSaved) {
          this.updateSearch()
        }

        if (discover) {
          this.summary = res
          this.discoverList = res.journalists
        } else {
          this.summaries.push({
            summary: '',
            clips: [],
            list: res.journalists,
          })

          this.$nextTick(() => {
            this.scrollToSummariesTop()
          })
        }
      } catch (e) {
        console.log(e)
        this.loading = false
        this.secondaryLoader = false
        if (this.chatting) {
          this.responseEmpty = true
        }
      } finally {
        this.loading = false
        this.secondaryLoader = false
        console.log(this.summaries)

        if (discover) {
          this.scrollToTop()
        }
        this.refreshUser()
      }
    },
    async saveWritingStyle() {
      this.savingStyle = true
      try {
        const res = await Comms.api.saveWritingStyle({
          example: this.sample,
          title: this.styleName,
        })

        this.$toast('Writing style saved', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.writingStyle = this.sample
        this.writingStyleTitle = this.styleName
        this.refreshUser()
      } catch (e) {
        console.log(e)
      } finally {
        this.sample = ''
        this.styleName = ''
        this.getWritingStyles()
        this.savingStyle = false
        this.toggleLearnInputModal('')
      }
    },
    toggleLearnInputModal(txt) {
      if (txt) {
        this.sample = txt.replace(/<\/?[^>]+(>|$)/g, '').trim()
      }
      this.inputModalOpen = !this.inputModalOpen
      this.showingStyles = false
    },
    toggleDetailsInputModal() {
      this.detailsInputModalOpen = !this.detailsInputModalOpen
      this.hideMainDetails()
      this.showingDetails = false
    },
    addWritingStyle(ex, title) {
      this.writingStyle = ex
      this.writingStyleTitle = title
      this.showingStyles = false
      this.showingWritingStyles = false

      if (this.chatting) {
        this.secondResponse = title
        this.scrollToChatTop()
      }
    },
    async rewritePitchWithStyle(ex, title) {
      this.writingStyle = ex
      this.writingStyleTitle = title
      this.loadingPitch = true
      this.hideStylesEmail()
      try {
        const res = await Comms.api.rewritePitch({
          original: this.revisedPitch,
          style: ex,
          with_style: true,
        })
        const body = res.body
        const signature = this.user.emailSignature ? this.user.emailSignature : ''
        const html = `<p>${body.replace(/\n/g, '</p><p>\n')} ${signature.replace(
          /\n/g,
          '</p><p>',
        )}  </p>`
        const quill = this.$refs.quill.quill
        quill.clipboard.dangerouslyPasteHTML(html)
        this.loadingPitch = false
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingPitch = false
        this.drafting = false
      }
    },
    async rewritePitchWithDetails(title, deets) {
      if (title === this.detailTitle) {
        this.detailTitle = ''
        this.selectedOrg = ''
        this.showingDetailsEmail = false
        this.showingAllDetails = false
      }
      this.selectedOrg = deets
      this.detailTitle = title
      this.showingDetailsEmail = false
      this.showingAllDetails = false
      this.loadingPitch = true
      try {
        const res = await Comms.api.rewritePitch({
          original: deets,
          bio: this.currentJournalistBio,
          style: this.writingStyle,
          journalist: this.currentJournalist,
        })

        // this.targetEmail = res.email

        const body = res.body

        const signature = this.user.emailSignature ? this.user.emailSignature : ''
        const html = `<p>${body.replace(/\n/g, '</p><p>\n')} ${signature.replace(
          /\n/g,
          '</p><p>',
        )}  </p>`.trim()
        const quill = this.$refs.quill.quill
        quill.clipboard.dangerouslyPasteHTML(html)
        this.subject = res.subject
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingPitch = false
        this.drafting = false
      }
    },
    addDetails(title, deets) {
      if (!this.isViewOnly) {
        if (title === this.detailTitle) {
          this.detailTitle = ''
          this.selectedOrg = ''
          this.showingDetails = false
          this.showingMainDetails = false
          this.showingAllDetails = false
        }
        this.selectedOrg = deets
        this.detailTitle = title
        this.showingDetails = false
        this.showingMainDetails = false
        this.showingAllDetails = false
      }
    },
    addDetailsAlt(title, deets) {
      if (title === this.detailTitle) {
        this.detailTitle = ''
        this.selectedOrg = ''
        this.showCompanySelection = false
      }
      this.selectedOrg = deets
      this.detailTitle = title
      this.showCompanySelection = false
      this.showingDetails = false
      if (this.chatting) {
        this.userResponse = title
      }
    },
    clearDetails() {
      this.currentDetails = ''
      this.detailTitle = ''
      this.selectedOrg = ''
      this.showingDetails = false
      this.showingMainDetails = false
      this.showingAllDetails = false
      this.showCompanySelection = false
    },
    setIndex(i) {
      this.hoverIndex = i
    },
    // setDetailIndex(i) {
    //   this.detailIndex === i
    // },
    // removeDetailIndex() {
    //   this.detailIndex === null
    // },
    changeJournalistName(i) {
      this.journalistIndex = i
      this.showingName = true
    },
    removeNameIndex() {
      this.journalistIndex = 475
      this.showingName = false
    },
    removeIndex() {
      this.hoverIndex = null
    },
    toggleStyles() {
      this.personalStyles = !this.personalStyles
    },
    pitchStyleSetup() {
      const style = `You are an AI PR assistant with the ability to create perfect, engaging content for any format. Your writing is modern, informal, and conversational—ideal for Millennial and Gen Z audiences. You excel at storytelling, using subtle persuasion without ever sounding salesy, and can adapt your tone and structure seamlessly to fit different content types.

To replicate the author's style, focus on the following guidelines:

Language: Relatable and conversational, never robotic or overly formal. Avoid jargon but maintain a polished feel.
Storytelling: Start with a strong hook, craft a compelling narrative, and conclude with an impactful ending.

Tone Adaptation: Adjust your style based on the content type:

Media Pitch: Short, under 150 words, breezy, intriguing, and tailored to the recipient. Open with Hi {journalist} followed by a relevant observation about the author and why this story is a fit for their readers.

Press Release: Professional yet warm and accessible. Emphasize key statistics and link them to industry trends. Use an attention-grabbing headline, crucial details early on, and compelling quotes. Aim for an engaging narrative that appeals to journalists.

Social Media Copy: Short, snappy, and aligned with trends.

Blog Post: Personal, insightful, and easy to digest.

Avoid Hard Sells: Focus on authenticity and building trust through storytelling rather than direct calls to action.

Persuasion: Use emotional and logical appeals subtly, guiding the reader naturally to a conclusion.

Your goal is to create content that resonates deeply, connects authentically, and compels action without being overt. Every word should feel like it was written by a human, unrecognizable by AI detectors.`
      this.writingStyle = style
      this.writingStyleTitle = 'Default'
    },

    writeSetup() {
      const style = `You are an AI PR assistant with the ability to create perfect, engaging content for any format. Your writing is modern, informal, and conversational—ideal for Millennial and Gen Z audiences. You excel at storytelling, using subtle persuasion without ever sounding salesy, and can adapt your tone and structure seamlessly to fit different content types.

To replicate the author's style, focus on the following guidelines:

Language: Relatable and conversational, never robotic or overly formal. Avoid jargon but maintain a polished feel.
Storytelling: Start with a strong hook, craft a compelling narrative, and conclude with an impactful ending.

Tone Adaptation: Adjust your style based on the content type:

Media Pitch: Short, under 150 words, breezy, intriguing, and tailored to the recipient. Open with Hi {journalist} followed by a relevant observation about the author and why this story is a fit for their readers.

Press Release: Professional yet warm and accessible. Emphasize key statistics and link them to industry trends. Use an attention-grabbing headline, crucial details early on, and compelling quotes. Aim for an engaging narrative that appeals to journalists.

Social Media Copy: Short, snappy, and aligned with trends.

Blog Post: Personal, insightful, and easy to digest.

Avoid Hard Sells: Focus on authenticity and building trust through storytelling rather than direct calls to action.

Persuasion: Use emotional and logical appeals subtly, guiding the reader naturally to a conclusion.

Your goal is to create content that resonates deeply, connects authentically, and compels action without being overt. Every word should feel like it was written by a human, unrecognizable by AI detectors.`
      this.writingStyle = style
      this.writingStyleTitle = 'Default'
    },
    toggleWritingStyles() {
      this.showingWritingStyles = !this.showingWritingStyles
    },
    hideWritingStyles() {
      this.showingWritingStyles = false
    },
    hideStyles() {
      this.showingStyles = false
    },
    hideStylesEmail() {
      this.showingStylesEmail = false
    },
    hideDetails() {
      this.showingDetails = false
    },
    hideMainDetails() {
      this.showingMainDetails = false
    },
    hideDetailsEmail() {
      this.showingDetailsEmail = false
    },
    toggleShowStyles() {
      this.showingStyles = !this.showingStyles
      this.scrollToChatTop()
    },
    toggleShowStylesEmail() {
      this.showingStylesEmail = !this.showingStylesEmail
    },
    toggleShowDetails() {
      this.showingDetails = !this.showingDetails
    },
    toggleShowDetailsEmail() {
      this.showingDetailsEmail = !this.showingDetailsEmail
    },
    toggleMainDetails() {
      if (!this.isViewOnly) {
        this.showingMainDetails = !this.showingMainDetails
      }
    },
    toggleHelpMenu() {
      this.showingHelp = !this.showingHelp
    },
    closeHelp() {
      this.showingHelp = false
    },
    selectSuggestion(txt) {
      this.newTemplate = txt
      this.showSuggestions = false
    },
    selectChatSuggestion(txt) {
      this.chatSearch = txt
      this.hideJournalistSuggestions()
    },
    selectReportSuggestion(txt) {
      this.chatSearch = txt
      this.hideJournalistSuggestions()
    },
    toggleSuggestions() {
      this.showSuggestions = !this.showSuggestions
    },
    hideSuggestions() {
      this.showSuggestions = false
    },
    hideArticleDropdown() {
      this.showArticleGenerateDropdown = false
    },
    toggleDate() {
      if (!this.isViewOnly) {
        this.showDateSelection = !this.showDateSelection
        this.showingSources = false
        this.showCompanySelection = false
      }
    },
    toggleCompany() {
      this.showCompanySelection = !this.showCompanySelection
      this.showingSources = false
      this.showDateSelection = false
    },
    hideCompany() {
      this.showCompanySelection = false
    },
    hideDate() {
      this.showDateSelection = false
    },
    hideSources() {
      this.showingSources = false
    },
    insertAltTweetCitations(text, i) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)
        const citation = this.summaries[i].clips.length
          ? this.summaries[i].clips[citationIndex]
          : this.filteredTweets[citationIndex]

        if (citation) {
          if (citation.type !== 'twitter') {
            return `
        <sup>
          <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

                <span class="span-row">
            <img height="16px" width="16px" src="${
              citation.type === 'youtube'
                ? `${this.youtubePlaceholder}`
                : `${this.blueskyPlaceholder}`
            }" alt="">
               <span class="c-elip">
                ${citation.author}      
              </span>
            </span>

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-elip " href="${citation.url}" target="_blank" >${
              citation.text ? citation.text : citation.title
            }</a>
              </span>
               <img src="${
                 citation.image_url ? citation.image_url : this.blueskyPlaceholder
               }" height="40px" width="40px" alt="">
              </span>
              
              
             
            </span>
          </span>   
        </sup>
      `
          } else {
            return `
        <sup>
          <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
             <span class="span-row">
              <img height="16px" width="16px" src="${this.twitterPlaceholder}" alt="">
               <span class="c-elip">
                ${citation.user.username}      
              </span>
            </span>

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-blue c-elip " href="https://twitter.com/${citation.user.username}/status/${citation.id}}" target="_blank" >${citation.text}</a>
              </span>
               <img src="${citation.user.profile_image_url}" height="40px" width="40px" alt="">
              </span>
              
              
            
              <span class="c-elip-small pointer select-journalist-alt" summary-index='${i}' data-citation='${citationIndex}'>
              By ${citation.user.username}
              </span>
             
            </span>
          </span>   
        </sup>
      `
          }
        }
        return match
      })
    },
    insertTweetCitations(text) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)
        const citation = this.tweets[citationIndex]
        if (citation) {
          if (citation.type !== 'twitter') {
            return `
        <sup>
          <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

            <span class="span-row">
            <img height="16px" width="16px" src="${
              citation.type === 'youtube'
                ? `${this.youtubePlaceholder}`
                : `${this.blueskyPlaceholder}`
            }" alt="">
               <span class="c-elip">
                ${citation.author}      
              </span>
            </span>
             

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-blue c-elip" href="${citation.url}" target="_blank" >${
              citation.text ? citation.text : citation.title
            }</a>
              
                </span>
               <img src="${
                 citation.image_url ? citation.image_url : this.blueskyPlaceholder
               }" height="40px" width="40px" alt="">
              </span>      
            
            
             
            </span>
          </span>
        </sup>
      `
          } else {
            return `
        <sup>
          <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

            <span class="span-row">
              <img height="16px" width="16px" src="${this.twitterPlaceholder}" alt="">
               <span class="c-elip">
                ${citation.user.username}      
              </span>
            </span>
             

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-elip c-blue" href="https://twitter.com/${citation.user.username}/status/${citation.id}" target="_blank" >${citation.text}</a>
              
                </span>
               <img src="${citation.user.profile_image_url}" height="40px" width="40px" alt="">
              </span>      
            
              <span class="c-elip-small cursor select-journalist" data-citation='${citationIndex}'>
              By ${citation.user.username}
              </span>
             
            </span>
          </span>
        </sup>
      `
          }
        }
        return match
      })
    },
    insertAltOmniCitations(text, i) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)

        const citation = this.summaries[i].clips.length
          ? this.summaries[i].clips[citationIndex]
          : this.omniResults[citationIndex]

        if (citation) {
          if (citation.hasOwnProperty('type')) {
            if (citation.type !== 'twitter') {
              return `
        <sup>
          <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

            <span class="span-row">
            <img height="16px" width="16px" src="${
              citation.type === 'youtube'
                ? `${this.youtubePlaceholder}`
                : `${this.blueskyPlaceholder}`
            }" alt="">
               <span class="c-elip">
                ${citation.author}      
              </span>
            </span>
             

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-blue c-elip" href="${citation.url}" target="_blank" >${
                citation.text ? citation.text : citation.title
              }</a>
              
                </span>
               <img src="${
                 citation.image_url ? citation.image_url : this.blueskyPlaceholder
               }" height="40px" width="40px" alt="">
              </span>      
            
            
             
            </span>
          </span>
        </sup>
      `
            } else {
              return `
        <sup>
          <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

            <span class="span-row">
              <img height="16px" width="16px" src="${this.twitterPlaceholder}" alt="">
               <span class="c-elip">
                ${citation.user.username}      
              </span>
            </span>
             

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-elip c-blue" href="https://twitter.com/${citation.user.username}/status/${citation.id}" target="_blank" >${citation.text}</a>
              
                </span>
               <img src="${citation.user.profile_image_url}" height="40px" width="40px" alt="">
              </span>      
            
              <span class="c-elip-small cursor select-journalist-alt" summary-index='${i}' data-citation='${citationIndex}'>
              By ${citation.user.username}
              </span>
             
            </span>
          </span>
        </sup>
      `
            }
          } else if (citation.hasOwnProperty('snippet')) {
            return `
        <sup>

         <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source}      
              </span>

              <span class="row">
                <span class="col">
               
               <a class="inline-link c-elip c-blue" href="${citation.link}" target="_blank" >${citation.title}</a>

            


                </span>
               <img src="${citation.image}" height="40px" width="40px" alt="">
              </span>
              
              
            
              <span class="c-elip-small select-journalist-alt" summary-index='${i}' data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>

         
        </sup>
      `
          } else {
            return `
        <sup>
          <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source.name ? citation.source.name : citation.source}      
              </span>

              <span class="row">
                <span class="col">
                
                <a class="inline-link c-elip c-blue" href="${
                  citation.url ? citation.url : citation.link
                }" target="_blank" >${citation.title}</a>

              

                </span>


                <img src="${
                  citation.image ? citation.image : citation.image_url
                }" height="40px" width="40px" alt="">

                </span>
              
              
            
              <span class="c-elip-small select-journalist-alt" summary-index='${i}' data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>
        </sup>
      `
          }
        }
        return match
      })
    },

    insertOmniCitations(text) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)

        const citation = this.omniResults[citationIndex]

        if (citation) {
          if (citation.hasOwnProperty('type')) {
            if (citation.type !== 'twitter') {
              return `
        <sup>
          <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

            <span class="span-row">
            <img height="16px" width="16px" src="${
              citation.type === 'youtube'
                ? `${this.youtubePlaceholder}`
                : `${this.blueskyPlaceholder}`
            }" alt="">
               <span class="c-elip">
                ${citation.author}      
              </span>
            </span>
             

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-blue c-elip" href="${citation.url}" target="_blank" >${
                citation.text ? citation.text : citation.title
              }</a>
              
                </span>
               <img src="${
                 citation.image_url ? citation.image_url : this.blueskyPlaceholder
               }" height="40px" width="40px" alt="">
              </span>      
            
            
             
            </span>
          </span>
        </sup>
      `
            } else {
              return `
        <sup>
          <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">

            <span class="span-row">
              <img height="16px" width="16px" src="${this.twitterPlaceholder}" alt="">
               <span class="c-elip">
                ${citation.user.username}      
              </span>
            </span>
             

              <span class="row">
                <span class="col">
               
              <a class="inline-link c-elip c-blue" href="https://twitter.com/${citation.user.username}/status/${citation.id}" target="_blank" >${citation.text}</a>
              
                </span>
               <img src="${citation.user.profile_image_url}" height="40px" width="40px" alt="">
              </span>      
            
              <span class="c-elip-small cursor select-journalist" data-citation='${citationIndex}'>
              By ${citation.user.username}
              </span>
             
            </span>
          </span>
        </sup>
      `
            }
          } else if (citation.hasOwnProperty('snippet')) {
            return `
        <sup>

         <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source}      
              </span>

              <span class="row">
                <span class="col">
               
               <a class="inline-link c-elip c-blue" href="${citation.link}" target="_blank" >${citation.title}</a>

            


                </span>
               <img src="${citation.image}" height="40px" width="40px" alt="">
              </span>
              
              
            
              <span class="c-elip-small  select-journalist" data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>

         
        </sup>
      `
          } else {
            return `
        <sup>
          <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source.name ? citation.source.name : citation.source}      
              </span>

              <span class="row">
                <span class="col">
                
                <a class="inline-link c-elip c-blue" href="${
                  citation.url ? citation.url : citation.link
                }" target="_blank" >${citation.title}</a>

              

                </span>


                <img src="${
                  citation.image ? citation.image : citation.image_url
                }" height="40px" width="40px" alt="">

                </span>
              
              
            
              <span class="c-elip-small select-journalist" data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>
        </sup>
      `
          }
        }
        return match
      })
    },

    insertAltNewsCitations(text, i) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)
        const citation = this.summaries[i].clips.length
          ? this.summaries[i].clips[citationIndex]
          : this.filteredArticles[citationIndex]

        if (citation) {
          return `
        <sup>

          <span class="citation-wrapper-alt" >

            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>

            <span class="citation-tooltip">

              <span class="c-elip">
                ${citation.source.name ? citation.source.name : citation.source}      
              </span>

              <span class="row">
                <span class="col">   
                  <a class="inline-link c-elip c-blue" href="${
                    citation.link ? citation.link : citation.url
                  }" target="_blank">${citation.title}</a>
                  
                </span>

               <img src="${
                 citation.image_url ? citation.image_url : citation.image
               }" height="40px" width="40px" alt="">
              </span>
              
            
              <span class="c-elip-small select-journalist-alt" summary-index='${i}' data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>

          </span>
    
        </sup>
      `
        }
        return match
      })
    },
    insertAltWebCitations(text, i) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)
        const citation = this.summaries[i].clips.length
          ? this.summaries[i].clips[citationIndex]
          : this.googleResults[citationIndex]

        if (citation) {
          return `
        <sup>


           <span class="citation-wrapper-alt" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source}      
              </span>

              <span class="row">
                <span class="col">
               
                 <a class="inline-link c-elip c-blue" href="${citation.link}" target="_blank" >${citation.title}</a>

              


                </span>
               <img src="${citation.image}" height="40px" width="40px" alt="">
              </span>
              
              
            
              <span class="c-elip-small select-journalist-alt" summary-index='${i}' data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>


         
        </sup>
      `
        }
        return match
      })
    },
    insertNewsCitations(text) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)
        const citation = this.filteredArticles[citationIndex]
        if (citation) {
          return `
        <sup>
          <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source.name ? citation.source.name : citation.source}      
              </span>

              <span class="row">
                <span class="col">
                
                <a class="inline-link c-elip c-blue" href="${
                  citation.url ? citation.url : citation.link
                }" target="_blank" >${citation.title}</a>

              

                </span>


                <img src="${
                  citation.image ? citation.image : citation.image_url
                }" height="40px" width="40px" alt="">

                </span>
              
              
            
              <span class="c-elip-small select-journalist" data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>
        </sup>
      `
        }
        return match
      })
    },
    insertCitations(text) {
      return text.replace(/\[(\d+)\]/g, (match, p1) => {
        const citationIndex = parseInt(p1)
        const citation = this.googleResults[citationIndex]
        if (citation) {
          return `
        <sup>

         <span class="citation-wrapper" >
            <a  class="citation-link citation-link-alt">
            <img class="inline-svg" src="${this.citationSvg}" alt="">
            </a>
            <span class="citation-tooltip">
              <span class="c-elip">
                ${citation.source}      
              </span>

              <span class="row">
                <span class="col">
               
               <a class="inline-link c-elip c-blue" href="${citation.link}" target="_blank" >${citation.title}</a>

            


                </span>
               <img src="${citation.image}" height="40px" width="40px" alt="">
              </span>
              
              
            
              <span class="c-elip-small  select-journalist" data-citation='${citationIndex}'>
              By ${citation.author}
              </span>
             
            </span>
          </span>

         
        </sup>
      `
        }
        return match
      })
    },
    validateDate(event) {
      const userInput = event.target.value

      const minDate = this.mainView === 'news' ? this.minDate : this.minDateSocial

      if (userInput < minDate) {
        this.dateStart = minDate
      }
    },
    modeReset() {
      this.loading = true
      this.summary = ''
      this.originalSearch = ''
      this.noResultsString = 'No results found. Try a different request'
      this.alternateAricles = []
      this.followUps = []
      this.summaries = []
      this.latestArticles = []
      this.latestMedia = []
      this.addedClips = []
      this.filteredArticles = []
      this.googleResults = []
      this.addedArticles = []
      this.tweets = []
      this.posts = []
      this.searchSaved = false
    },
    toggleType(type) {
      if (!this.isViewOnly) {
        this.modeReset()
        if (type === 'social') {
          this.mainView = type
          this.generateNewSearch(null, false)
          this.clearSearchText()
          this.notifiedList = []

          //  else {
          //   this.goToIntegrations()
          // }
        } else if (type === 'write') {
          this.getWritingStyles()
          this.mainView = type
          this.generateNewSearch(null, false)
        } else {
          this.mainView = type
          this.generateNewSearch(null, false)
          this.clearSearchText()
          this.notifiedList = []
        }
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
    searchJournalist(event) {
      if (event.target.tagName === 'STRONG') {
        const text = event.target.innerText
        this.searchArticleText = text
        this.searchTweetText = text
        this.searchResultText = text
        this.scrollToTopDivider()
      }
    },
    clearSearchText() {
      this.searchArticleText = ''
      this.searchTweetText = ''
      this.searchResultText = ''
      this.searchChannelText = ''
    },
    toggleRelevant() {
      if (!this.showingRelevant) {
        this.showingRelevant = true
        if (!this.relevantData) {
          this.getRelevantArticles()
        }
      } else if (this.showingRelevant) {
        this.showingRelevant = false
      }
    },
    toggleJournalists() {
      if (!this.showingJournalists) {
        this.showingJournalists = true
        if (!this.journalistData) {
          this.listTopJournalists()
        }
      } else if (this.showingJournalists) {
        this.showingJournalists = false
      }
    },
    // toggleJournalistsList() {
    //   if (!this.showingJournalistsList) {
    //     this.showingJournalistsList = true
    //     if (!this.journalistListData) {
    //       //  getJournalistfunction here
    //     }
    //   } else if (this.showingJournalistsList) {
    //     this.showingJournalistsList = false
    //   }
    // },
    toggleRelated() {
      if (!this.showingRelated) {
        this.showingRelated = true
        if (!this.relatedTopics.length) {
          this.getRelatedTopics()
        }
      } else if (this.showingRelated) {
        this.showingRelated = false
      }
    },
    scrollToTop() {
      setTimeout(() => {
        this.$refs.loadedContent.scrollTop = 0
      }, 300)
    },
    scrollToSummariesTop() {
      const latestIndex = this.summaries.length - 1

      if (this.$refs['summary-' + latestIndex]) {
        this.$refs['summary-' + latestIndex][0].scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        })
      }
    },
    async getRelevantArticles() {
      let clips = []
      this.loadingRelevant = true
      if (this.mainView === 'news') {
        clips = this.getArticleDescriptions(this.filteredArticles)
      } else {
        clips = this.prepareTweetSummary(this.tweets)
      }
      try {
        const res = await Comms.api.getRelevantArticles({
          term: this.newSearch,
          clips: clips,
          social: this.mainView === 'social' ? true : false,
        })
        this.relevantData = res.data.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingRelevant = false
      }
    },
    async listTopJournalists() {
      let clips = []
      this.loadingJournalists = true
      if (this.mainView === 'news') {
        clips = this.getArticleDescriptions(this.filteredArticles)
      } else {
        clips = this.prepareTweetSummary(this.tweets)
      }
      try {
        const res = await Comms.api.listTopJournalists({
          term: this.newSearch,
          clips: clips,
          social: this.mainView === 'social' ? true : false,
        })
        this.journalistData = res.data.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingJournalists = false
      }
    },
    async getRelatedTopics() {
      let clips = []
      this.loadingRelated = true
      if (this.mainView === 'news') {
        clips = this.getArticleDescriptions(this.filteredArticles)
      } else if (this.mainView === 'web') {
        clips = this.googleResults
      } else {
        clips = this.prepareTweetSummary(this.tweets)
      }

      try {
        const res = await Comms.api.getRelatedTopics({
          clips: clips,
        })

        const str = res.data

        let lines = str.split('\n')

        for (let i = 0; i < lines.length; i++) {
          if (lines[i].startsWith('Search')) {
            if (lines[i + 1]) {
              this.relatedTopics.push(lines[i + 1].trim())
            }
          }
        }
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingRelated = false
      }
    },
    async exploreTopics() {
      this.loadingTopics = true
      try {
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingTopics = false
      }
    },

    async saveContactAlt() {
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
        setTimeout(() => {
          this.$toast('Contact saved to your Network', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }, 500)
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
        setTimeout(() => {
          this.savingContact = false
          this.bioModalOpen = false
        }, 500)
      }
    },

    async saveContact() {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }
      this.savingContact = true

      if (!this.targetEmail.includes('@')) {
        this.targetEmail = this.currentJournalist.replace(/\s+/g, '') + '@gmail.com'
        console.log(this.targetEmail)
      }
      try {
        const res = await Comms.api.addContact({
          user: this.user.id,
          email: this.targetEmail,
          journalist: this.currentJournalist,
          bio: this.currentJournalistBio,
          images: this.currentJournalistImages,
          outlet: this.currentPublication,
        })
        this.$toast('Successfully saved contact to Network', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.buttonClicked = true
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
      }
    },

    async getJournalistBioDiscover() {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }

      this.loadingDraft = true
      this.targetEmail = ''
      try {
        const res = await Comms.api.getJournalistBio({
          journalist: this.currentJournalist,
          outlet: this.currentPublication,
          company: this.selectedOrg,
          search: false,
        })
        this.targetEmail = res.data.email

        if (!this.targetEmail) {
          let fakeEmail = this.currentJournalist + '@' + this.currentPublication + '.com'
          this.targetEmail = fakeEmail.replace(/\s+/g, '')
        }
        this.currentJournalistImages = res.data.images
        this.currentJournalistBio = res.data.bio.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        this.currentPublication = res.data.company
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingDraft = false
        this.refreshUser()
      }
    },

    async getJournalistBioAlt() {
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
        this.contactName = res.data.name
        this.targetEmail = res.data.email
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

    async getJournalistBio(social = false) {
      this.loadingDraft = true
      this.targetEmail = ''

      try {
        const res = await Comms.api.getJournalistBio({
          journalist: this.currentJournalist,
          outlet: this.currentPublication,
          company: this.selectedOrg,
          search: true,
          social: social,
        })

        this.targetEmail = res.data.email

        if (!this.targetEmail) {
          let fakeEmail = this.currentJournalist + '@' + this.currentPublication + '.com'
          this.targetEmail = fakeEmail.replace(/\s+/g, '')
        }

        this.currentJournalistImages = res.data.images
        this.currentJournalistBio = res.data.bio.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        this.currentPublication = res.data.company

        this.$nextTick(() => {
          this.refreshUser()
        })
        this.refreshUser()
      } catch (e) {
        console.error(e)
      } finally {
        this.loadingDraft = false
      }
    },

    async copyBioText() {
      try {
        const cleanedBio = this.currentJournalistBio.replace(/<\/?[^>]+(>|$)/g, '')
        await navigator.clipboard.writeText(cleanedBio)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    toggleGoogleModal() {
      this.googleModalOpen = !this.googleModalOpen
    },
    toggleSources() {
      this.showingSources = !this.showingSources
      this.showDateSelection = false
      this.showCompanySelection = false
    },
    toCamelCase(text) {
      return text.charAt(0).toUpperCase() + text.slice(1)
    },
    async verifyEmail() {
      this.verifying = true
      try {
        const res = await Comms.api.verifyEmail({
          email: this.targetEmail,
          journalist: this.currentJournalist,
          publication: this.currentPublication,
        })
        if (res.data.is_valid) {
          setTimeout(() => {
            this.emailVerified = true
          }, 500)
          if (res.data.email) {
            this.targetEmail = res.data.email
          }
        } else {
          this.emailError = true
        }
      } catch (e) {
        console.error(e)
        this.emailError = true
      } finally {
        this.refreshUser()
        setTimeout(() => {
          this.verifying = false
        }, 200)
      }
    },
    toggleEmailJournalistModal() {
      if (!this.loadingPitch && !this.sendingEmail && !this.verifying) {
        this.emailJournalistModalOpen = !this.emailJournalistModalOpen
      }
    },
    async createDraft() {
      this.drafting = true
      try {
        const res = await Comms.api.createDraft({
          subject: this.subject,
          body: this.revisedPitch,
          recipient: this.targetEmail,
          name: this.currentJournalist,
        })
        this.emailJournalistModalOpen = false
        this.$toast('Draft created', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.revisedPitch = ''
        this.sendingEmail = false
        this.drafting = false
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
    async sendEmail() {
      this.sendingEmail = true
      try {
        const res = await Comms.api.sendEmail({
          subject: this.subject,
          body: this.revisedPitch,
          recipient: this.targetEmail,
          name: this.currentJournalist,
          cc: this.ccEmail,
          bcc: this.bccEmail,
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
        this.refreshUser()
      }
    },
    openDraftPitch() {
      this.googleModalOpen = false
      this.emailJournalistModalOpen = true
      this.draftPitch()
    },
    async draftPitch() {
      this.loadingPitch = true
      try {
        if (this.mainView !== 'write' && this.mainView !== 'discover') {
          const res = await Comms.api.draftPitch({
            user: this.user.firstName,
            org: this.selectedOrg,
            style: this.pitchStyle,
            bio: this.currentJournalistBio,
            author: this.currentJournalist,
            outlet: this.currentPublication,
            headline: this.currentHeadline,
            description: this.currentDescription,
            date: this.currentDate,
          })
          const body = res.data.replace(/^Subject(?: Line)?:[\s\S]*?\n|email:.*$/gim, '')
          const signature = this.user.emailSignature ? this.user.emailSignature : ''
          const html = `<p>${body.replace(/\n/g, '</p><p>\n')} ${signature.replace(
            /\n/g,
            '</p><p>',
          )}  </p>`

          const quill = this.$refs.quill.quill
          quill.clipboard.dangerouslyPasteHTML(html)
          this.subject = res.data.match(/^Subject(?: Line)?:(.*)\n/i)[1].trim()
          this.targetEmail = res.data.match(/email:\s*(.*)$/m)[1].trim()
        } else {
          const res = await Comms.api.rewritePitch({
            original: this.mainView !== 'write' ? this.summary : this.selectedOrg,
            bio: this.currentJournalistBio,
            style: this.writingStyle,
            journalist: this.currentJournalist,
          })
          console.log(res)
          this.targetEmail = res.email
          const body = res.body
          const signature = this.user.emailSignature ? this.user.emailSignature : ''
          const html = `<p>${body.replace(/\n/g, '</p><p>\n')} ${signature.replace(
            /\n/g,
            '</p><p>',
          )}  </p>`
          const quill = this.$refs.quill.quill
          quill.clipboard.dangerouslyPasteHTML(html)
          this.subject = res.subject
        }
        this.verifyEmail()
      } catch (e) {
        console.error(e)
      } finally {
        this.refreshUser()
        this.loadingPitch = false
      }
    },
    grabJournalist(name, pub) {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }
      this.currentJournalistBio = ''
      this.currentJournalistImages = []
      this.currentJournalist = name
      this.currentPublication = pub
      this.googleModalOpen = true
      this.getJournalistBioDiscover()
    },
    extractNameEmailTip(text) {
      const name = text
        .match(/Name:\s*(.*)/)[1]
        .trim()
        .replace(/<strong>|<\/strong>/g, '')

      // Check for either "Outlet" or "Company"
      const publicationMatch = text.match(/(Outlet|Company):\s*(.*)/)
      const publication = publicationMatch
        ? publicationMatch[2].trim().replace(/<strong>|<\/strong>/g, '')
        : ''

      const tip = text
        .match(/Reason for Selection:\s*(.*)/)[1]
        .trim()
        .replace(/<strong>|<\/strong>/g, '')

      return { name, publication, tip }
    },
    selectJournalist(article, web = false) {
      if (!this.isViewOnly) {
        if (this.mainView === 'web') {
          const author = article.author
          const outlet = article.source
          const headline = article.title
          const description = article.snippet
          const rawDate = new Date()
          const date = this.getTimeDifferenceInMinutes(rawDate)

          this.currentHeadline = headline
          this.currentDescription = description
          this.currentJournalist = author
          this.currentPublication = outlet
          this.currentDate = date

          this.googleModalOpen = true
          this.getJournalistBio()

          // this.draftPitch(author, outlet, headline, description, date)
        } else if (this.mainView === 'news' || this.mainView === 'trending') {
          const author = this.extractJournalist(article.author)
          const outlet = this.mainView === 'trending' ? article.source : article.source.name
          const headline = article.title
          const description = article.description
          const date = this.getTimeDifferenceInMinutes(
            this.mainView === 'trending' ? article.date : article.publish_date,
          )
          this.googleModalOpen = true
          // this.emailJournalistModalOpen = true
          this.currentHeadline = headline
          this.currentDescription = description
          this.currentJournalist = author
          this.currentPublication = outlet
          this.currentDate = date
          this.getJournalistBio()
          // this.draftPitch(author, outlet, headline, description, date)
        } else if (this.mainView === 'omni') {
          if (article.hasOwnProperty('snippet')) {
            const author = article.author
            const outlet = article.source
            const headline = article.title
            const description = article.snippet
            const rawDate = new Date()
            const date = this.getTimeDifferenceInMinutes(rawDate)

            this.currentHeadline = headline
            this.currentDescription = description
            this.currentJournalist = author
            this.currentPublication = outlet
            this.currentDate = date

            this.googleModalOpen = true
            this.getJournalistBio()
          } else if (article.hasOwnProperty('type')) {
            const author =
              article.type !== 'twitter'
                ? article.author
                : article.user.name + ' ' + '@' + article.user.username
            const outlet =
              article.type === 'youtube'
                ? 'YouTube'
                : article.type === 'bluesky'
                ? 'Bluesky social media page'
                : 'not available'
            const headline =
              article.type === 'youtube'
                ? 'Youtube Channel'
                : article.type === 'bluesky'
                ? 'Bluesky User'
                : 'X/Twitter User'
            const description = article.text
            const date = this.getTimeDifferenceInMinutes(article.created_at)
            this.googleModalOpen = true
            // this.emailJournalistModalOpen = true
            this.currentHeadline = headline
            this.currentDescription = description
            this.currentJournalist = author
            this.currentPublication = outlet
            this.currentDate = date
            this.getJournalistBio(true)
          } else {
            const author = this.extractJournalist(article.author)
            const outlet = this.mainView === 'trending' ? article.source : article.source.name
            const headline = article.title
            const description = article.description
            const date = this.getTimeDifferenceInMinutes(
              this.mainView === 'trending' ? article.date : article.publish_date,
            )
            this.googleModalOpen = true
            // this.emailJournalistModalOpen = true
            this.currentHeadline = headline
            this.currentDescription = description
            this.currentJournalist = author
            this.currentPublication = outlet
            this.currentDate = date
            this.getJournalistBio()
          }
        } else {
          const author =
            article.type !== 'twitter'
              ? article.author
              : article.user.name + ' ' + '@' + article.user.username
          const outlet =
            article.type === 'youtube'
              ? 'YouTube'
              : article.type === 'bluesky'
              ? 'Bluesky social media page'
              : 'not available'
          const headline =
            article.type === 'youtube'
              ? 'Youtube Channel'
              : article.type === 'bluesky'
              ? 'Bluesky User'
              : 'X/Twitter User'
          const description = article.text
          const date = this.getTimeDifferenceInMinutes(article.created_at)
          this.googleModalOpen = true
          // this.emailJournalistModalOpen = true
          this.currentHeadline = headline
          this.currentDescription = description
          this.currentJournalist = author
          this.currentPublication = outlet
          this.currentDate = date
          this.getJournalistBio(true)
        }
      } else {
      }
    },
    extractJournalist(author) {
      if (!author) {
        author = 'Unknown Author'
      } else {
        if (author.includes(',')) {
          author = author.split(',')[0]
        }
        const authorParts = author.trim().split(' ')
        if (authorParts.length === 3) {
          author = `${authorParts[0]} ${authorParts[2]}`
        } else if (authorParts.length === 2) {
          author = `${authorParts[0]} ${authorParts[1]}`
        }
      }

      return author
    },
    extractNameAndEmail(text) {
      // Split text by whitespace to extract name and email
      const parts = text.trim().split(/\s+/)
      let name = ''
      let email = ''

      parts.forEach((part) => {
        if (part.includes('@')) {
          email = part.replace(/[()<>]/g, '')
        } else {
          name += part + ' '
        }
      })

      name = name.trim()

      return { name, email }
    },
    goTo(post, index) {
      const postIndex = this.posts.findIndex((p) => p === post)
      if (postIndex !== -1) {
        this.$set(this.posts[postIndex], 'currentIndex', index)
        this.$forceUpdate()
      }
    },
    goToIg(link) {
      window.open(link, '_blank')
    },
    removeHashtags() {
      this.newSearch = this.newSearch.replace(/#/g, '')
    },
    formattedPostDate(timestamp) {
      const dateObj = new Date(timestamp)

      const month = dateObj.getMonth() + 1
      const day = dateObj.getDate()
      const year = dateObj.getFullYear()

      const formattedMonth = month < 10 ? '0' + month : month
      const formattedDay = day < 10 ? '0' + day : day

      const formattedDate = `${formattedMonth}-${formattedDay}-${year}`

      return formattedDate
    },
    formattedNumber(number) {
      if (number) {
        let numStr = number.toString()
        return numStr.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
      } else {
        return 0
      }
    },
    extractHashtag(hashtag) {
      const parts = hashtag.split(/[.\n]/)
      return parts[0]
    },
    openFilePicker() {
      if (!this.summaryLoading) {
        this.$refs.fileInput.click()
      }
    },

    async summarizePdf(instructions) {
      if (!this.selectedFile) {
        console.log('select file first')
        return
      }
      this.summaryLoading = true
      this.showingPromptDropdown = false
      this.showSummaryMenu = false
      try {
        let formData = new FormData()
        formData.append('instructions', instructions ? instructions : 'Summarize the data')
        if (this.selectedFile && this.selectedFile instanceof File) {
          formData.append('pdf_file', this.selectedFile)
        } else {
          console.error('This is not a File object')
        }
        await Comms.api.summarizePDF(formData).then((res) => {
          this.summary = res.content
        })
      } catch (e) {
        // `${e.data.error}`

        this.$toast(`Unable to process. PDF too long or text not readable.`, {
          timeout: 3500,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        // this.selectedFile = null
        this.summaryLoading = false
      }
    },
    handleFileUpload(event) {
      this.summary = ''
      this.selectedFile = event.target.files[0]
    },
    // in case we need file type verification on the server
    uploadPDF() {
      if (!this.selectedFile) {
        console.log('No file selected')
        return
      }
      const formData = new FormData()
      formData.append('pdfFile', this.selectedFile)

      axios
        .post('uploadEndpoint', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then((response) => {
          console.log('File uploaded successfully', response.data)
        })
        .catch((error) => {
          console.error('Error uploading file', error)
        })
    },
    toggleSummaryMenu() {
      this.showSummaryMenu = !this.showSummaryMenu
    },
    setNewSearch(txt) {
      if (!this.isViewOnly) {
        this.newSearch = txt
        this.highlightCurlyBracketText()
      }
    },
    highlightCurlyBracketText() {
      this.$nextTick(() => {
        const textarea = document.getElementById('search-input')
        const start = this.newSearch.indexOf('{')
        const end = this.newSearch.indexOf('}') + 1

        if (start !== -1 && end !== -1) {
          textarea.focus()
          textarea.setSelectionRange(start, end)
        }
      })
    },
    setAndSearch(txt) {
      this.newSearch = txt
      this.generateNewSearch(null, false)
    },
    setNewSummary(txt) {
      this.newTemplate = txt
    },
    selectPrompt(prompt) {
      this.newTemplate = prompt
      this.togglePromptModal()
    },
    toggleDateDropdown() {
      this.dateOpen = !this.dateOpen
    },
    goToIntegrations() {
      this.$router.push({ name: 'PRIntegrations' })
    },
    goToPage(page) {
      this.$router.push({ name: page })
    },
    toggleSaveModal() {
      this.saveModalOpen = !this.saveModalOpen
    },
    async savePitch() {
      this.savingSearch = true
      try {
        const response = await Comms.api.savePitch({
          name: this.pitchName || this.pitch.slice(0, 60),
          user: this.user.id,
          type: this.newSearch,
          audience: '',
          generated_pitch: this.summary,
          instructions: this.newTemplate,
        })
        if (response.id) {
          this.searchId = response.id
          this.$toast('Content saved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.savedPitch = true

          await this.$store.dispatch('getPitches')
        }
      } catch (e) {
        console.log(e)
      } finally {
        this.savingSearch = false
        this.showingSave = false
      }
    },
    async saveDiscovery() {
      this.savingSearch = true

      try {
        const res = await Comms.api.saveDiscovery({
          user: this.user.id,
          name: this.listName,
          content: this.newSearch,
          type: this.newSearch,
          beat: 'beat',
          location: 'location',
          list: 'list',
          results: this.discoverList,
        })

        if (res.id) {
          this.$toast('List saved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.savedDiscovery = true

          this.getDiscoveries()
        }
      } catch (e) {
        console.log(e)
        this.$toast(`${e}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.savingSearch = false
        this.showingSave = false
      }
    },

    changeEmailText() {
      if (!this.isPaid) {
        this.emailText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultEmailText() {
      if (!this.isPaid) {
        this.emailText = 'Activate Alerts'
      } else {
        return
      }
    },
    setCurrentAlert(id = null) {
      console.log('email alerts - >', this.emailAlerts)
      if (id) {
        this.currentAlert = this.emailAlerts.filter((alert) => alert.search === id)[0]
      } else {
        this.currentAlert = this.emailAlerts.filter(
          (alert) =>
            alert.search === this.searchId ||
            alert.thread === this.threadId ||
            alert.thread === this.searchId,
        )[0]

        console.log('currentalert', this.currentAlert)
      }

      // this.getEmailAlerts()
    },
    async testEmailAlert() {
      try {
        Comms.api.testEmailAlert({
          alert_id: this.currentAlert.id,
          social: this.mainView === 'social' ? true : false,
        })
        this.showingSave = false
        this.$toast('Preview sent', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      }
    },
    async removeEmailAlert() {
      try {
        const res = await Comms.api.removeEmailAlert({ id: this.currentAlert.id })
        this.hideSave()
        this.$toast('Digest removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })

        this.$nextTick(() => {
          this.getEmailAlerts()
          this.refreshUser()
        })
      } catch (e) {
        console.log(e)
      }
    },
    async getEmailAlerts() {
      try {
        const response = await Comms.api.getEmailAlerts()
        let threadList = []
        let searchList = []
        this.emailAlerts = response.results
        threadList = response.results.map((alert) => alert.thread)
        searchList = response.results.map((alert) => alert.search)
        this.notifiedList = [...threadList, ...searchList]
      } catch (e) {
        console.log(e)
      }
    },
    setAlertTime() {
      let alert = this.emailAlerts.filter((alert) => alert.thread === this.threadId)[0]

      if (alert) {
        const datetimeString = alert.run_at

        let date = new Date(datetimeString)

        let hours = date.getHours()
        let minutes = date.getMinutes()
        let ampm = hours >= 12 ? 'PM' : 'AM'

        hours = hours % 12
        hours = hours ? hours : 12

        this.searchTime = `${hours.toString().padStart(2, '0')}:${minutes
          .toString()
          .padStart(2, '0')} ${ampm} `
      } else {
        return
      }
    },

    setCurrentAlertTime(alert) {
      // console.log(this.alertTIme)
      // console.log(alert.run_at)

      const datetimeString = this.alertTIme

      let date = new Date(datetimeString)

      let hours = date.getHours()
      let minutes = date.getMinutes()
      let ampm = hours >= 12 ? 'PM' : 'AM'

      hours = hours % 12
      hours = hours ? hours : 12

      this.searchTime = `${this.alertTIme} ${ampm}`
    },
    // sendtoslack
    async addEmailAlert() {
      this.savingAlert = true

      try {
        await this.createSearch()
        const response = await Comms.api.addEmailAlert({
          search: this.searchId,
          thread: this.threadId,
          run_at: this.formattedDate,
          user: this.user.id,
          title: this.savedSearch.title || this.searchName,
          type: this.alertType,
          recipients: [this.alertChannel ? this.alertChannel : this.user.email],
        })
        this.currentAlert = response
        this.currentAlertId = response.id

        this.getEmailAlerts()
        this.showingSave = false
        this.setCurrentAlertTime(response)
        this.$toast('Successfully scheduled Daily Digest', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        if (e.data.error) {
          this.$toast(`${e.data.error}`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Error sending content, try again later', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        this.savingAlert = false
      }
    },
    calculateDate(selectedTime) {
      const [hours, minutes] = selectedTime.split(':').map(Number)

      if (
        isNaN(hours) ||
        isNaN(minutes) ||
        hours < 0 ||
        hours > 23 ||
        minutes < 0 ||
        minutes > 59
      ) {
        this.formattedDate = 'Invalid time input'
        return
      }

      const currentDate = new Date()
      currentDate.setHours(hours, minutes, 0, 0)

      const year = currentDate.getFullYear()
      const month = String(currentDate.getMonth() + 1).padStart(2, '0')
      const day = String(currentDate.getDate()).padStart(2, '0')
      const formattedTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(
        2,
        '0',
      )}:00.000000`

      this.formattedDate = `${year}-${month}-${day}T${formattedTime}`
    },
    toggleNotifyModal() {
      if (!this.isPaid) {
        this.openPaidModal('Upgrade your plan to activate alerts')
        return
      } else if ((this.searchSaved || this.savedSearch) && this.isPaid) {
        this.alertSet = false
        this.notifyModalOpen = !this.notifyModalOpen
      }
    },
    closeContentModal() {
      if (!this.contentLoading) {
        this.contentModalOpen = false
      } else {
        return
      }
    },
    setRow(i) {
      this.currentRow = i
    },
    setAddedClips(clips) {
      this.addedClips = clips
    },
    removeRow() {
      this.currentRow = null
    },
    toggleArticleGenerateDropdown() {
      this.showArticleGenerateDropdown = !this.showArticleGenerateDropdown
    },
    toggleGenerateDropdown() {
      this.showGenerateDropdown = !this.showGenerateDropdown
    },
    selectOption(val, index) {
      if (!this.contentLoading) {
        this.optionIndex = index
        this.contentLoading = true
        this.selectedOption = val
        this.setPitchContent()
      }
    },
    selectArticleOption(url, val, index) {
      if (!this.contentLoading) {
        this.contentInstructions = ''
        this.showGenerateDropdown = false
        this.showArticleGenerateDropdown = false
        this.contentModalOpen = true
        this.optionIndex = index
        this.contentUrl = url
        this.contentType = val
        if (val) {
          this.contentInstructions = `Create a ${val} for XXX, newsjacking this article`
        }

        // this.setArticlePitchContent(url,sum)
      }
    },
    closeSuccessModal() {
      this.$router.push({ name: 'PRSummaries' })
      this.$router.go()
      this.successModal = false
    },
    setPitchContent() {
      let content = {
        summary: this.summary,
        term: this.newSearch,
        type: this.selectedOption,
      }
      this.$store.commit('setGeneratedContent', content)
      setTimeout(() => {
        this.$router.push({ name: 'Pitches' })
      }, 500)
    },

    bindClickOutsidePromptMenu() {
      // Get the directive element where you want to bind the listener
      const el = document.getElementById('instructions')

      if (el) {
        // Define the clickOutsideHandler function (the same logic as in your directive)
        function clickOutsideHandler(e) {
          if (!el.contains(e.target)) {
            // Trigger your functionality when clicked outside the element
            this.hidePromptDropdown() // Replace with your actual functionality
          }
        }

        // Attach the clickOutsideHandler to the element
        el._clickOutsideHandler = clickOutsideHandler.bind(this)

        // Add the event listener to the document body
        document.body.addEventListener('click', el._clickOutsideHandler)
      }
    },
    setArticlePitchContent(sum) {
      let content = {
        summary: sum,
        term: this.newSearch,
        type: this.selectedOption,
      }
      this.$store.commit('setGeneratedContent', content)
      setTimeout(() => {
        this.$router.push({ name: 'Pitches' })
      }, 500)
    },
    removeArticle(title) {
      const newArticles = this.addedArticles.filter((article) => article.title !== title)
      this.addedArticles = newArticles
    },
    removeClip(title) {
      const cats = this.$store.state.categories
      if (Object.keys(cats).length) {
        const newCats = { ...cats }
        for (let key in cats) {
          const clips = cats[key]
          const filteredClips = clips.filter((clip) => clip.title !== title && clip.text !== title)
          newCats[key] = filteredClips
        }
        this.$store.dispatch('updateCategories', newCats)
      }
      const newClips = this.addedClips.filter((clip) => clip.title !== title && clip.text !== title)
      this.addedClips = newClips
      this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      if (this.currentSearch) {
        this.metaData = { ...this.currentSearch.meta_data, clips: newClips }
        // this.updateMetaData()
      }
    },
    toggleReport() {
      if (!this.isPaid) {
        this.openPaidModal('Upgrade your plan in order to create reports.')
      } else {
        this.ShowReport = !this.ShowReport
      }
    },
    async regenerateGoogleSearch(clips, instructions) {
      try {
        const res = await Comms.api.googleSearch({
          query: this.newSearch,
          instructions: instructions,
          summary: this.summary,
          results: clips,
          project: this.selectedOrg,
        })

        if (res.message.toLowerCase().includes('new search term')) {
          this.newSearch = this.extractTerm(res.message)
          this.secondaryLoader = false
          this.secondaryLoaderAlt = true
          this.googleSearch()
          if (this.searchSaved) {
            this.updateSearch()
          }
        } else {
          this.summaries.push({
            summary: res.message
              .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
              .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, ''),
            clips: res.results,
          })
          this.secondaryLoader = false
          this.secondaryLoaderAlt = false

          if (this.searchSaved) {
            this.updateSearch()
          }

          this.$nextTick(() => {
            this.scrollToSummariesTop()
          })

          setTimeout(() => {
            this.altCitationsMounted = true
          }, 5000)
        }

        this.secondaryLoader = false
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    async googleSearch() {
      // this.resetAll()
      this.citationsMounted = false
      if (!this.newSearch) {
        return
      }
      if (!this.chatting) {
        this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      }
      if (!this.summary) {
        this.loading = true
      }

      try {
        const res = await Comms.api.googleSearch({
          query: this.newSearch,
          instructions: this.newTemplate,
          project: this.selectedOrg,
        })
        this.searchResponseText = ' '
        this.searchResponseText = ''
        this.googleText = res.article

        if (!this.summary) {
          this.googleResults = res.results
          this.summary = res.message
            .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
            .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, '')
        } else {
          this.summaries.push({
            summary: res.message
              .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
              .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, ''),
            clips: res.results,
          })
          this.secondaryLoader = false
          this.secondaryLoaderAlt = false

          this.$nextTick(() => {
            this.scrollToSummariesTop()
          })
        }

        this.$nextTick(() => {
          this.refreshUser()
        })
      } catch (e) {
        this.googleResults = []
        this.summary = ''
        console.log(e)
        this.showingArticles = false
      } finally {
        if (!this.summary) {
          this.scrollToTop()
        }

        this.loading = false
        if (this.chatting) {
          this.changeSearch({ search: this.newSearch, template: this.newTemplate })
        }
      }
    },
    async generatePitch() {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }

      if (!this.newSearch) {
        return
      }
      if (!this.chatting) {
        this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      }
      this.loading = true
      if (this.chatting) {
        this.scrollToChatTop()
      }
      try {
        const res = await Comms.api.generatePitch({
          type: this.newSearch,
          instructions: this.selectedOrg,
          style: this.writingStyle,
        })
        this.summary = res.pitch.replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        this.$store.commit('setGeneratedContent', null)
        this.refreshUser()
        this.$store.dispatch('getPitches')
        this.scrollToTop()
        this.savedPitch = false
      } catch (e) {
        console.log('ERROR CREATING PITCH', e)
      } finally {
        // this.refreshUser()
        this.loading = false
        this.scrollToTop()

        if (this.chatting) {
          this.chatting = false
          this.changeSearch({ search: this.booleanString, template: this.newTemplate })
        }
      }
    },

    async uploadArticle() {
      this.resetAll()
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      this.clipLoading = true
      try {
        await Comms.api
          .uploadLink({
            url: this.uploadLink,
          })
          .then((response) => {
            this.success = true
            this.addClipFromUrl(response)
            this.articleBanner('Article added!')
          })
      } catch (e) {
        this.addedArticles = []
        this.success = false
        console.log(e)
        this.articleBanner('Error adding article!')
      } finally {
        this.clipLoading = false
        this.uploadLink = null
      }
    },
    articleBanner(text) {
      this.articleBannerText = text
      this.showArticleBanner = true
      setTimeout(() => {
        this.showArticleBanner = false
      }, 2000)
    },
    addClipFromUrl(clip) {
      clip.author = clip.author[0]
      clip['search'] = this.newSearch
      this.addedArticles = [clip]
      this.getSourceSummary()
    },
    addClip(clip) {
      if (Array.isArray(clip.author)) {
        clip.author = clip.author[0]
      }
      clip['search'] = this.newSearch
      if (this.addedClips && this.addedClips.length < 20) {
        this.addedClip = true
        setTimeout(() => {
          this.addedClip = false
        }, 500)
        if (!clip.image_url && (clip.attachments || clip.edit_history_tweet_ids)) {
          let tweetImg = ''
          if (clip.attachments) {
            for (let i = 0; i < this.tweetMedia.length; i++) {
              const media = this.tweetMedia[i]
              if (media.media_key === clip.attachments.media_keys[0]) {
                if (media.type === 'photo') {
                  tweetImg = media.url
                  break
                } else if (media.type === 'video') {
                  // tweetImg = media.variants[1].url
                  // break;
                } else if (media.type === 'animated_gif') {
                  // tweetImg = media.variants[0].url
                  // break;
                }
              }
            }
          }
          if (!tweetImg) {
            tweetImg = clip.user.profile_image_url
          }
          clip.image_url = tweetImg
        }
        if (clip.attachments) {
          const mediaURLs = []
          for (let i = 0; i < clip.attachments.media_keys.length; i++) {
            const mediaKey = clip.attachments.media_keys[i]
            const media = this.tweetMedia.filter((tm) => tm.media_key === mediaKey)
            if (media[0]) {
              if (media[0].url) {
                mediaURLs.push({ url: media[0].url, type: 'image' })
              } else if (media[0].variants) {
                if (media[0].type === 'video') {
                  mediaURLs.push({ url: media[0].variants[1].url, type: 'video' })
                } else if (media[0].type === 'animated_gif') {
                  mediaURLs.push({ url: media[0].variants[0].url, type: 'animated_gif' })
                }
              }
            }
          }
          clip.attachments.mediaURLs = mediaURLs
        }
        const categories = this.$store.state.categories
        const categoryNames = Object.keys(categories)
        if (categoryNames.length) {
          clip.category = categoryNames[categoryNames.length - 1]
          categories[categoryNames[categoryNames.length - 1]].push(clip)
          this.$store.dispatch('updateCategories', categories)
        } else {
          clip.category = null
          this.addedClips.push(clip)
          this.$store.dispatch('updateCurrentReportClips', this.addedClips)
        }
        if (this.currentSearch) {
          this.metaData = { ...this.currentSearch.meta_data, clips: this.addedClips }
          // this.updateMetaData()
        }
      } else {
        return
      }
    },
    editClip(title, summary) {
      let clip = this.addedClips.filter((clip) => clip.title === title)[0]
      clip['summary'] = summary
      const newClips = this.addedClips.filter((clip) => clip.title !== title)
      newClips.unshift(clip)
      this.addedClips = newClips
      this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      if (this.currentSearch) {
        this.metaData = { ...this.currentSearch.meta_data, clips: newClips }
        // this.updateMetaData()
      }
    },
    soonButtonText() {
      this.buttonText = 'Coming Soon!'
    },
    defaultButtonText() {
      this.buttonText = 'Article Summary'
    },
    openTweet(username, id) {
      window.open(`https://twitter.com/${username}/status/${id}`, '_blank')
    },
    openTweetAlt(url) {
      window.open(`${url}`, '_blank')
    },
    addSuggestion(ex) {
      this.newSearch = ex
      this.hideDropdown()
    },
    addPromptSuggestion(ex) {
      this.newTemplate = ex
      this.hidePromptDropdown()
    },
    // async copyArticleSummary(article) {
    //   try {
    //     const cleanedSummary = article
    //       .split('<strong>')
    //       .filter((item) => item !== '<strong>')
    //       .join('')
    //       .split('</strong>')
    //       .filter((item) => item !== '</strong>')
    //       .join('')
    //     await navigator.clipboard.writeText(cleanedSummary)
    //     this.copyTip = 'Copied!'

    //     setTimeout(() => {
    //       this.copyTip = 'Copy'
    //     }, 2000)
    //   } catch (err) {
    //     console.error('Failed to copy text: ', err)
    //   }
    // },
    // async copyText() {
    //   try {
    //     const cleanedSummary = this.summary
    //       .split('<strong>')
    //       .filter((item) => item !== '<strong>')
    //       .join('')
    //       .split('</strong>')
    //       .filter((item) => item !== '</strong>')
    //       .join('')
    //     await navigator.clipboard.writeText(cleanedSummary)
    //     this.copyTip = 'Copied!'

    //     setTimeout(() => {
    //       this.copyTip = 'Copy'
    //     }, 2000)
    //   } catch (err) {
    //     console.error('Failed to copy text: ', err)
    //   }
    // },
    async copyDiscoverTextAlt(list) {
      try {
        // Extract and clean the text from each object in discoverList
        const cleanedSummary = list
          .map((item) => {
            // Clean each property of HTML tags
            const name = item.name.replace(/<\/?[^>]+(>|$)/g, '')
            const publication = item.publication.replace(/<\/?[^>]+(>|$)/g, '')
            const reason = item.reason.replace(/<\/?[^>]+(>|$)/g, '')

            // Concatenate the cleaned properties
            return `${name} - ${publication}: ${reason}`
          })
          .join('\n') // Join all the text into a single string, each object on a new line

        // Copy the cleaned text to the clipboard
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        // Reset the copyTip after 2 seconds
        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyDiscoverText() {
      try {
        // Extract and clean the text from each object in discoverList
        const cleanedSummary = this.discoverList
          .map((item) => {
            // Clean each property of HTML tags
            const name = item.name.replace(/<\/?[^>]+(>|$)/g, '')
            const publication = item.publication.replace(/<\/?[^>]+(>|$)/g, '')
            const reason = item.reason.replace(/<\/?[^>]+(>|$)/g, '')

            // Concatenate the cleaned properties
            return `${name} - ${publication}: ${reason}`
          })
          .join('\n') // Join all the text into a single string, each object on a new line

        // Copy the cleaned text to the clipboard
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        // Reset the copyTip after 2 seconds
        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyTextAlt(txt) {
      try {
        const cleanedSummary = txt.replace(/<\/?[^>]+(>|$)/g, '')
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyText() {
      try {
        const cleanedSummary = this.summary.replace(/<\/?[^>]+(>|$)/g, '')
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyShareThread() {
      try {
        await navigator.clipboard.writeText(this.savedSearch.share_url)
        this.copyShareTip = 'Copied!'
        setTimeout(() => {
          this.copyShareTip = 'Copy Link'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyArticleSummary(article) {
      try {
        const cleanedSummary = article.replace(/<\/?[^>]+(>|$)/g, '')
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    showDropdown() {
      this.showingDropdown = true
    },
    hideDropdown() {
      this.showingDropdown = false
    },
    showPromptDropdown() {
      this.showingPromptDropdown = true
    },
    hidePromptDropdown() {
      this.showingPromptDropdown = false
    },
    resetAll() {
      this.clearNewSearch()
      this.omniNews = []
      this.altOmniNews = []
      this.omniSocial = []
      this.altOmniSocial = []
      this.omniWeb = []
      this.altOmniWeb = []
      this.searchingType = 'news'
      this.booleanString = null
      this.chatting = false
      this.userResponse = null
      this.journalistInfo = ''
      this.newSearch = ''
      this.originalSearch = ''
      this.noResultsString = 'No results found. Try a different request'
      this.alternateAricles = []
      this.followUps = []
      this.summaries = []
      this.latestArticles = []
      this.latestMedia = []
      this.addedClips = []
      this.filteredArticles = []
      this.googleResults = []
      this.addedArticles = []
      this.tweets = []
      this.posts = []
      this.metaData = { clips: [] }
      this.changeSearch(null)
      this.$store.dispatch('setSearch', null)
      this.summary = ''
      this.tweetError = ''
      this.showSummaryMenu = false
      this.showingRelated = false
      this.showingJournalists = false
      this.showingRelevant = false
      this.relevantData = ''
      this.journalistData = ''
      this.relatedTopics = []
      this.showingSources = false
      this.journalisListtData = ''
      this.searchSaved = false
      this.followupShares = null
      this.totalShares = null
      this.notifiedList = []
      this.secondaryLoaderAlt = false
      this.secondaryLoader = false
      this.hideShare()
    },
    resetSearch() {
      this.clearNewSearch()
      this.addedClips = []
      // this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      this.metaData = { clips: [] }
      this.$emit('change-search', null)
      this.$store.dispatch('setSearch', null)
      this.summary = ''
    },
    switchMainView(view) {
      if (!this.isViewOnly) {
        this.resetAll()
        this.clearDetails()
        if (view !== this.mainView) {
          this.mainView = view
          this.$store.dispatch('updateListName', view)
        }
      }
    },
    formatNumber(num) {
      if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B'
      }
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
      }
      return num.toString()
    },
    toggleArticleRegenerate() {
      this.showArticleRegenerate = !this.showArticleRegenerate
    },
    toggleSaveName() {
      this.showSaveName = !this.showSaveName
    },
    setSearch(search) {
      this.omniNews = search.meta_data.omniNews
      this.omniResults = search.meta_data.omniResults
      this.omniWeb = search.meta_data.omniWeb
      this.altOmniNews = search.meta_data.altOmniNews
      this.altOmniSocial = search.meta_data.altOmniSocial
      this.altOmniWeb = search.meta_data.altOmniWeb
      this.omniSocial = search.meta_data.omniSocial
      this.citationsMounted = false
      this.altCitationsMounted = false
      this.savedSearch = search
      this.shareUrl = search.share_url
      this.threadId = search.id
      this.newSearch = search.meta_data.searchTerm
      this.summary = search.meta_data.summary
      this.discoverList = search.meta_data.list
      this.summaries = search.meta_data.summaries
      this.followUps = search.meta_data.followUps
      this.preparedTweets = search.meta_data.preparedTweets
      this.tweets = search.meta_data.tweets ? search.meta_data.tweets : []
      this.googleResults = search.meta_data.googleResults
      this.articlesFiltered = search.meta_data.articlesFiltered
      this.filteredArticles = search.meta_data.filteredArticles
      this.filteredResults = search.meta_data.filteredResults
      this.tweetMedia = search.meta_data.tweetMedia
      this.originalSearch = search.meta_data.originalSearch
      this.mainView = search.meta_data.type
      this.totalShares = search.meta_data.totalShares
      this.followupShares = search.meta_data.followupShares
      this.searchSaved = true
      this.booleanString = search.meta_data.boolean
        ? search.meta_data.boolean
        : search.meta_data.searchTerm
      this.changeSearch({ search: this.booleanString, template: this.newTemplate })

      setTimeout(() => {
        this.citationsMounted = true
        this.altCitationsMounted = true
      }, 3000)
      // this.summarizing = false
      // this.searchName = search.name
      this.setAlertTime()
      // this.showSummaryInstructions = true
      // if (search.hasOwnProperty('audience')) {
      //   this.newTemplate = search.instructions
      //   this.summary = search.generated_pitch
      //   this.newSearch = search.type
      //   this.savedPitch = true
      // } else if (search.hasOwnProperty('location')) {
      //   console.log(search)
      //   this.newTemplate = search.content
      //   this.summary = search.list
      //   this.discoverList = search.results
      //   this.newSearch = search.type || search.name
      //   this.savedDiscovery = true
      // } else {
      //   this.newSearch = search.input_text
      //   this.newTemplate = search.instructions
      //   this.booleanString = search.search_boolean
      //   this.metaData = search.meta_data
      //   this.summary = ''
      //   this.addedClips = this.$store.state.currentReportClips
      // }

      // this.mainView =
      //   search.search_boolean === 'Ig'
      //     ? 'instagram'
      //     : search.type === 'SOCIAL_MEDIA'
      //     ? 'social'
      //     : search.type === 'NEWS'
      //     ? 'news'
      //     : search.hasOwnProperty('audience')
      //     ? 'write'
      //     : search.hasOwnProperty('location')
      //     ? 'discover'
      //     : ''
      // if (this.mainView !== 'write' && this.mainView !== 'discover') {
      //   this.generateNewSearch(null, true, search.search_boolean)
      // } else {
      //   this.changeSearch(search.type)
      // }
      this.setCurrentAlert()
    },
    changeIndex() {
      setTimeout(() => {
        this.isTyping = false
        this.typedMessage = ''
      }, 5750)
      setTimeout(() => {
        this.updateMessage()
      }, 5850)
    },
    updateMessage() {
      this.textIndex = Math.floor(Math.random() * this.searchMessages.length)
      this.isTyping = true
      this.typedMessage = this.searchMessages[this.textIndex]
    },
    scrollToTopDivider() {
      setTimeout(() => {
        this.$refs.topDivider.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    },
    removeSource() {
      this.additionalSources = ''
      this.addingSources = !this.addingSources
    },
    removePrompt() {
      this.newTemplate = ''
      this.addingPrompt = !this.addingPrompt
    },
    toggleAddPrompt() {
      this.addingPrompt = !this.addingPrompt
    },
    toggleAddSource() {
      this.addingSources = !this.addingSources
    },
    getTimeDifferenceInMinutes(dateString) {
      if (dateString) {
        const currentDate = new Date()
        const givenDate = new Date(dateString)

        if (
          givenDate.getDate() === currentDate.getDate() &&
          givenDate.getMonth() === currentDate.getMonth() &&
          givenDate.getFullYear() === currentDate.getFullYear()
        ) {
          const timeDifferenceInMilliseconds = currentDate - givenDate
          const timeDifferenceInMinutes = Math.floor(timeDifferenceInMilliseconds / (1000 * 60))
          if (timeDifferenceInMinutes >= 60) {
            const timeDifferenceInHours = Math.floor(timeDifferenceInMinutes / 60)
            const remainingMinutes = timeDifferenceInMinutes % 60
            return `${timeDifferenceInHours}h`
          } else {
            return `${timeDifferenceInMinutes}m`
          }
        } else {
          let month
          let day
          let year
          if (Number(givenDate.getMonth() + 1)) {
            month = givenDate.getMonth() + 1
          } else {
            month = '--'
          }
          if (Number(givenDate.getDate())) {
            day = givenDate.getDate()
          } else {
            day = '--'
          }
          if (Number(givenDate.getFullYear())) {
            year = givenDate.getFullYear()
          } else {
            year = '--'
          }
          // return `${month}/${day}/${year}`
          return `${month}/${day}`
        }
      } else {
        return '--/--/'
      }
    },
    openPaidModal(msg) {
      this.upgradeMessage = msg
      this.paidModal = true
    },
    closePaidModal() {
      this.paidModal = false
    },
    goToContact() {
      window.open('https://managr.ai/contact', '_blank')
    },
    stopLoading() {
      this.loading = false
      this.summaryLoading = false
    },
    closeDropDowns() {
      if (this.dateOpen) {
        this.toggleDateDropdown()
      }
    },
    toggleDropdowns() {
      this.expandedView = !this.expandedView
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatWindow = this.$refs.loadedContent
        chatWindow.scrollTo({
          top: chatWindow.scrollHeight,
          behavior: 'smooth',
        })
      })
    },
    scrollToChatTop() {
      this.$nextTick(() => {
        const chatWindow = this.$refs.chatWindow
        chatWindow.scrollTo({
          top: chatWindow.scrollHeight,
          behavior: 'smooth',
        })
      })
    },
    async generateChatSearch(event) {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }
      this.scrollToChatTop()
      if (event && event.shiftKey) {
        return
      }
      if (this.currentChat.view === 'news') {
        if (this.currentChat.details && (this.detailTitle || this.userResponse)) {
          this.newTemplate = this.currentChat.searchText + ' ' + this.selectedOrg
          this.secondResponse = this.chatSearch
          this.newSearch = this.chatSearch
          this.chatSearch = ''
          this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        } else {
          this.newSearch = this.chatSearch
          this.newTemplate = this.currentChat.searchText + ' ' + this.chatSearch
          this.userResponse = this.chatSearch
          this.chatSearch = ''
          this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
          this.loading = true
        }

        if (this.currentChat.details && !this.detailTitle) {
          this.selectedOrg = chatSearch
          this.userResponse = chatSearch
        } else {
          try {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            this.loading = true
            this.scrollToChatTop()
            await this.getClips(false, null, this.newTemplate)
            if (this.filteredArticles.length) {
              this.getSummary(
                this.filteredArticles,
                this.newTemplate ? this.newTemplate : this.newSearch,
                false,
                this.newTemplate ? this.newTemplate : '',
              )
            } else {
              this.responseEmpty = true
            }
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            this.refreshUser()
          } catch (e) {
            console.log(e)
          }
        }
      } else if (this.currentChat.view === 'write') {
        if (this.currentChat.details && !this.detailTitle) {
          this.selectedOrg = chatSearch
          this.userResponse = chatSearch
          return
        } else {
          this.newSearch = this.chatSearch
          this.thirdResponse = this.chatSearch
          this.chatSearch = ''
          this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
          this.generatePitch()
        }
      } else if (this.currentChat.view === 'web') {
        this.newSearch = this.chatSearch
        this.userResponse = this.chatSearch
        this.chatSearch = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.googleSearch()
      } else if (this.currentChat.view === 'discover') {
        this.newSearch = this.chatSearch
        this.userResponse = this.chatSearch
        this.chatSearch = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.discoverJournalists(true)
      } else if (this.currentChat.view === 'report') {
        if (this.urlsSet) {
          this.reportInstructions = this.chatSearch
          this.chatSearch = ''
          this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
          this.scrollToChatTop()
        } else {
          this.newSearch = this.chatSearch
          this.userResponse = this.chatSearch
          this.chatSearch = ''
          this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        }
      }
    },
    async generateNewSearch(event, saved = false, boolean = '') {
      if (event && event.shiftKey) {
        return
      }
      if (!this.summary) {
        this.filteredArticles = []
      }

      // this.tweets = []
      this.googleResults = []
      this.changeSearch(null)
      this.savedSearch = null
      this.showGenerateDropdown = false
      this.showingDropdown = false
      this.showSummaryMenu = false
      this.showingRelated = false
      this.showingJournalists = false
      this.showingRelevant = false
      this.relevantData = ''
      this.journalistData = ''
      this.relatedTopics = []
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }
      this.sendSummaryEmailText = 'Email'
      this.sentSummaryEmail = false
      this.addedClips = this.$store.state.currentReportClips
      if (this.shouldCancel) {
        return this.stopLoading()
      }
      if (this.mainView !== 'web' && (!this.newSearch || this.newSearch.length < 3)) {
        return
      } else if (this.mainView === 'social') {
        this.closeRegenModal()
        this.getTweets(saved)
      } else if (this.mainView === 'web') {
        this.closeRegenModal()
        this.googleSearch()
      } else if (this.mainView === 'omni') {
        this.closeRegenModal()
        this.omniSearch()
      } else if (this.mainView === 'trending') {
        if (!this.summary) {
          this.loading = true
        }

        this.changeSearch({ search: this.booleanString, template: this.newTemplate })

        try {
          if (this.shouldCancel) {
            return this.stopLoading()
          }

          await this.getTrendingClips(saved, boolean)

          if (saved) {
            this.updateSearch()
          }

          this.refreshUser()
        } catch (e) {
          console.log(e)
        }
      } else if (this.mainView === 'write') {
        this.closeRegenModal()
        this.generatePitch()
      } else if (this.mainView === 'discover') {
        this.closeRegenModal()
        this.discoverJournalists(true)
      } else {
        this.closeRegenModal()
        if (!this.summary && !this.originalSearch) {
          this.originalSearch = JSON.parse(JSON.stringify(this.newSearch))
        }
        if (!this.summary) {
          this.loading = true
        }

        this.changeSearch({ search: this.booleanString, template: this.newTemplate })
        try {
          if (this.shouldCancel) {
            return this.stopLoading()
          }
          await this.getClips(saved, boolean).then(() => {
            if (this.filteredArticles.length) {
              if (saved) {
                this.getSummary(this.filteredArticles, this.newTemplate)
              } else {
                this.getSummary(this.filteredArticles, this.newSearch)
              }
            }
          })
          if (this.shouldCancel) {
            return this.stopLoading()
          }
          if (saved) {
            this.updateSearch()
          }
          this.refreshUser()
        } catch (e) {
          console.log(e)
        }
      }
    },
    async getSourceSummary() {
      // this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      this.summaryLoading = true
      this.showingPromptDropdown = false
      this.showSummaryMenu = false
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        let response
        this.summary = ''
        if (this.addedArticles.length === 1) {
          response = await this.getArticleSummary(this.addedArticles[0].link, this.newTemplate)
          this.summary = response
        } else {
          response = await this.getSummary(this.addedArticles, this.newTemplate)
        }
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        if (this.searchSaved) {
          this.updateSearch()
        }
        this.refreshUser()
        this.summaryLoading = false
      } catch (e) {
        console.log(e)
      } finally {
        this.refreshUser()
        this.summarizing = true
      }
    },
    async updateMetaData() {
      try {
        await Comms.api
          .upateSearch({
            id: this.searchId,
            meta_data: this.metaData,
          })
          .then((response) => {
            this.savedSearch = {
              name: this.searchName,
              input_text: this.newSearch,
              meta_data: this.metaData,
              search_boolean: this.booleanString,
              instructions: this.newTemplate,
            }
            // this.$store.dispatch('setSearch', this.savedSearch)
          })
      } catch (e) {
        console.log('ERROR UPDATING SEARCH', e)
      }
    },
    updateSearch() {
      this.searchSaved = false
      // try {
      //   await Comms.api
      //     .upateSearch({
      //       id: this.searchId,
      //       name: this.searchName,
      //       input_text: this.newSearch,
      //       meta_data: this.metaData,
      //       search_boolean: this.booleanString,
      //       instructions: this.newTemplate,
      //     })
      //     .then((response) => {
      //       this.savedSearch = {
      //         name: this.searchName,
      //         input_text: this.newSearch,
      //         meta_data: this.metaData,
      //         search_boolean: this.booleanString,
      //         instructions: this.newTemplate,
      //       }

      //     })
      // } catch (e) {
      //   console.log('ERROR UPDATING SEARCH', e)
      // }
    },
    clearNewSearch() {
      // this.summary = null
      this.summarizing = false
      // this.newSearch = ''
      this.newTemplate = ''
      this.searchName = ''
      this.metaData = { clips: [] }
      this.addedArticles = []
    },
    openRegenModal() {
      this.regenModal = true
    },
    closeRegenModal() {
      this.regenModal = false
    },
    changeSearch(search) {
      this.selectedSearch = search
    },
    async createSearch() {
      try {
        const response = await Comms.api.createSearch({
          name: this.savedSearch.title,
          input_text: this.summaries.length
            ? this.followUps[this.followUps.length - 1]
            : this.newSearch,
          search_boolean: this.booleanString
            ? this.booleanString
            : this.summaries.length
            ? this.followUps[this.followUps.length - 1]
            : this.newSearch,
          instructions: this.summaries.length
            ? this.followUps[this.followUps.length - 1]
            : this.newSearch,
          meta_data: this.metaData,
          type: this.mainView === 'news' ? 'NEWS' : 'SOCIAL_MEDIA',
        })

        if (response.id) {
          this.searchId = response.id
          // this.$toast('Search Saved', {
          //   timeout: 2000,
          //   position: 'top-left',
          //   type: 'success',
          //   toastClassName: 'custom',
          //   bodyClassName: ['custom'],
          // })
        }
      } catch (e) {
        console.log(e)
      }
      // finally {
      //   this.$store.dispatch('getSearches')
      //   setTimeout(() => {
      //     this.saveModalOpen = false
      //     this.savingSearch = false
      //   }, 1000)
      // }
    },

    async sendSummaryEmail() {
      this.sendingSummaryEmail = true
      try {
        this.sentSummaryEmail = true

        // let clips
        // if (this.mainView === 'social') {
        //   clips = this.tweets.filter((clip, i) => {
        //     if (i < 10) {
        //       return clip
        //     }
        //   })
        // } else if (this.mainView === 'news') {
        //   clips = this.filteredArticles.filter((clip, i) => {
        //     if (i < 10) {
        //       return clip
        //     }
        //   })
        // } else {
        //   clips = this.addedArticles
        // }
        await Comms.api.sendSummaryEmail({
          link: this.currentAlert.share_url,
          title: this.newSearch,
          email: this.shareEmail,
        })
        this.sendSummaryEmailText = 'Sent!'
        this.$toast('Email sent!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log('Error in sendSummaryEmail:', e)
        this.sentSummaryEmail = false
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.showingShare = false
        this.sendingSummaryEmail = false
      }
    },
    abortFunctions() {
      this.shouldCancel = true

      for (let key in this.controllers) {
        this.controllers[key].controller.abort()
      }
      // update controllers here
      this.$store.dispatch('updateAbortController', {})
    },
    async getReportClips(urls) {
      try {
        const response = await Comms.api.getReportClips({
          urls: urls,
        })

        if (this.summary.length) {
          if (!response.length) {
            this.noResultsString = "We couldn't find any trending articles related to your search"
          }

          this.latestArticles = response.map((article) => {
            const shareEntry = this.followupShares.find(
              (share) => Object.keys(share)[0] === article.url,
            )
            const shares = shareEntry ? shareEntry[article.url] : 0
            return {
              ...article,
              author:
                Array.isArray(article.author) && article.author.length > 0
                  ? article.author[0]
                  : 'Unknown',
              shares: shares,
            }
          })
        } else {
          if (!response.length) {
            this.noResultsString = "We couldn't find any trending articles related to your search"
          }
          this.latestArticles = []
          this.filteredArticles = response.map((article) => {
            const shareEntry = this.totalShares.find(
              (share) => Object.keys(share)[0] === article.url,
            )
            const shares = shareEntry ? shareEntry[article.url] : 0
            return {
              ...article,
              author:
                Array.isArray(article.author) && article.author.length > 0
                  ? article.author[0]
                  : 'Unknown',
              shares: shares,
            }
          })
        }

        console.log(this.filteredArticles)
        this.loading = false
        this.getSummary(this.filteredArticles, this.newSearch)
      } catch (e) {
        console.error(e)
        this.loading = false
        this.$toast('Error gathering articles, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getTrendingClips(saved = false, boolean = '', chatTemplate = null) {
      this.showingDropdown = false
      if (this.summary) {
        this.scrollToBottom()
      }
      try {
        const response = await Comms.api.getTrendingClips({
          search: this.newSearch,
          countries: ['United States'],
        })

        if (!this.summary) {
          this.totalShares = response.articles.articles.map((art) => {
            return {
              [art.url]: art.total_shares,
            }
          })
        } else {
          this.followupShares = response.articles.articles.map((art) => {
            return {
              [art.url]: art.total_shares,
            }
          })
        }

        let urls = []

        urls = response.articles.articles.map((art) => {
          return art.url
        })

        if (this.summary.length) {
          if (!response.articles.articles.length) {
            this.noResultsString = 'No Articles found'
            this.showingArticles = false
          }
          this.getReportClips(urls)
        } else {
          if (!response.articles.articles.length) {
            this.noResultsString = 'No Articles found'
            this.showingArticles = false
          }
          this.latestArticles = []
          this.booleanString = response.string.string
          this.getReportClips(urls)
        }
        this.searchArticleText = ' '
        this.searchArticleText = ''
        this.booleanString = response.string

        if (!saved && !chatTemplate) {
          this.clearNewSearch()
        }
      } catch (e) {
        this.clearNewSearch()
        this.filteredArticles = []
        console.log(e)
      } finally {
        // this.loading = false
      }
    },
    async getClips(saved = false, boolean = '', chatTemplate = null) {
      // this.summary = null
      this.showingDropdown = false
      if (this.summary) {
        // this.secondaryLoaderAlt = false
        // this.secondaryLoader = true
        this.scrollToBottom()
      }
      try {
        // update controllers here
        this.$store.dispatch('updateAbortController', {
          ...this.$store.state.abortControllers,
          getClips: { name: 'getClips', controller: new AbortController() },
        })
        await Comms.api
          .getClips(
            {
              search: this.newSearch,
              boolean: boolean,
              user_id: this.user.id,
              date_from: this.dateStart,
              date_to: this.dateEnd,
              project: this.selectedOrg,
            },
            this.controllers.getClips.controller.signal,
          )
          .then((response) => {
            let urls = []
            if (this.summary.length) {
              if (!response.articles.length) {
                this.noResultsString = response.string
                this.showingArticles = false
              }
              this.latestArticles = response.articles
            } else {
              if (!response.articles.length) {
                this.noResultsString = response.string
                this.showingArticles = false
              }
              this.latestArticles = []
              this.filteredArticles = response.articles
            }

            urls = response.articles.map((art) => {
              return art.link
            })

            this.searchArticleText = ' '
            this.searchArticleText = ''
            this.booleanString = response.string

            if (!saved && !chatTemplate) {
              this.clearNewSearch()
            }
          })
      } catch (e) {
        this.clearNewSearch()
        this.filteredArticles = []
        console.log(e)
        this.showingArticles = false
      } finally {
        const newAbortControllers = { ...this.$store.state.abortControllers }
        delete newAbortControllers.getClips
        this.$store.dispatch('updateAbortController', newAbortControllers)
        this.loading = false
      }
    },
    async getOmniSummary() {
      let news = []
      let tweets = []
      let google = []

      // news = this.getArticleDescriptions(this.omniNews)
      // tweets = this.prepareTweetSummary(this.omniSocial)

      if (this.summary) {
        news = this.getArticleDescriptions(this.latestArticles)
        tweets = this.prepareTweetSummary(this.latestArticles)
        google = this.altOmniWeb
      } else {
        news = this.getArticleDescriptions(this.omniResults)
        tweets = this.prepareTweetSummary(this.omniResults)
        google = this.omniWeb
      }

      this.citationsMounted = false

      try {
        const response = await Comms.api.omniSummary({
          clips: news,
          social_data: tweets,
          web: google,
          search: this.newSearch,
          project: this.selectedOrg,
        })

        if (this.summary) {
          if (response.summary.toLowerCase().includes('new search term')) {
            this.newSearch = this.extractTerm(response.summary)
            this.secondaryLoader = false
            this.secondaryLoaderAlt = true
            this.generateNewSearch(null, false)
          } else {
            this.summaries.push({
              summary: response.summary
                .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
                .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>'),
              clips: this.latestArticles.length ? this.latestArticles : [],
            })
            this.secondaryLoader = false
            this.secondaryLoaderAlt = false

            this.$nextTick(() => {
              this.scrollToSummariesTop()
            })

            setTimeout(() => {
              this.altCitationsMounted = true
            }, 5000)
          }
        } else {
          this.summary = response.summary
            .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
        }

        this.loading = false
        this.summaryLoading = false
        this.searchingType = 'news'
        this.altOmniNews = []
        this.altOmniSocial = []
        this.altOmniWeb = []
        //  this.scrollToBottom()
      } catch (e) {
        console.log(e)
      }
    },

    async omniSearch() {
      let news = []
      let tweets = []
      let google = []

      if (!this.summary) {
        this.loading = true
      } else {
        this.scrollToBottom()
      }

      this.changeSearch({ search: this.newSearch, template: this.newTemplate })

      try {
        if (this.summary.length) {
          this.showingArticles = false

          const res = await Comms.api.getClips({
            search: this.newSearch,
            boolean: '',
            user_id: this.user.id,
            date_from: this.dateStart,
            date_to: this.dateEnd,
            project: this.selectedOrg,
          })

          this.altOmniNews = res.articles.slice(0, 30)
          this.booleanString = res.string

          //   this.summaryLoading = true
          this.searchingType = 'social'

          const socialRes = await Comms.api.getTweets({
            search: this.newSearch,
            user_id: this.user.id,
            project: this.selectedOrg,
            query: this.newSearch,
            date_from: this.dateStart,
            date_to: this.dateEnd,
          })

          this.altOmniSocial = socialRes.data.slice(0, 15)
          this.searchingType = 'web'

          const webRes = await Comms.api.googleSearch({
            query: this.newSearch,
            instructions: this.newTemplate,
            project: this.selectedOrg,
            omni: true,
          })

          this.altOmniWeb = webRes.results.slice(0, 5)
          this.altWebIndexStart = this.altOmniNews.length + this.altOmniSocial.length
          this.altOmniWeb = this.altOmniWeb.map((obj) => ({
            ...obj,
            citationIndex: obj.citationIndex + this.altWebIndexStart,
          }))

          this.latestArticles = this.altOmniNews.concat(this.altOmniSocial, this.altOmniWeb)
          this.searchingType = 'summary'
        } else {
          this.showingArticles = false
          this.latestArticles = []

          const res = await Comms.api.getClips({
            search: this.newSearch,
            boolean: '',
            user_id: this.user.id,
            date_from: this.dateStart,
            date_to: this.dateEnd,
            project: this.selectedOrg,
          })

          this.omniNews = res.articles.slice(0, 30)
          this.booleanString = res.string

          this.loading = false
          this.summaryLoading = true
          this.searchingType = 'social'

          const socialRes = await Comms.api.getTweets({
            search: this.newSearch,
            user_id: this.user.id,
            project: this.selectedOrg,
            query: this.newSearch,
            date_from: this.dateStart,
            date_to: this.dateEnd,
          })

          this.omniSocial = socialRes.data.slice(0, 15)
          this.searchingType = 'web'

          const webRes = await Comms.api.googleSearch({
            query: this.newSearch,
            instructions: this.newTemplate,
            project: this.selectedOrg,
            omni: true,
          })

          this.omniWeb = webRes.results.slice(0, 5)
          this.webIndexStart = this.omniNews.length + this.omniSocial.length
          this.omniWeb = this.omniWeb.map((obj) => ({
            ...obj,
            citationIndex: obj.citationIndex + this.webIndexStart,
          }))

          this.omniResults = this.omniNews.concat(this.omniSocial, this.omniWeb)
          this.searchingType = 'summary'
        }

        this.getOmniSummary()
      } catch (e) {
        console.log(e)
      }
    },
    async getTweets(saved = false) {
      // this.summary = null

      if (!this.summary) {
        this.loading = true
      } else {
        this.scrollToBottom()
      }

      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        const res = await Comms.api.getTweets({
          search: this.newSearch,
          user_id: this.user.id,
          project: this.selectedOrg,
          query: this.newSearch,
          date_from: this.dateStart,
          date_to: this.dateEnd,
        })

        if (this.summary.length) {
          if (!res.data.length) {
            this.noResultsString = res.string
            this.tweetMedia = []
            this.showingArticles = false
          }
          this.booleanString = res.string
          this.latestArticles = res.data
          if (res.includes) {
            this.latestMedia = res.includes.media
          }

          this.getTweetSummary()
        } else {
          if (!res.data.length) {
            this.noResultsString = res.string
            this.showingArticles = false
          }

          this.latestArticles = []
          this.latestMedia = []
          this.tweets = res.data
          if (res.includes) {
            this.tweetMedia = res.includes.media
          }

          this.getTweetSummary()
        }

        // if (this.summary.length) {
        //   if (!res.data.length) {
        //     this.noResultsString = 'No results. Try again'
        //     this.tweetMedia = []
        //   }
        //   this.booleanString = 'boolean'
        //   this.latestArticles = res.data
        //   this.latestMedia = {}

        //   this.getTweetSummary()
        // } else {
        //   if (!res.data.length) {
        //     this.noResultsString = 'No results. Try again'
        //   }

        //   this.latestArticles = []
        //   this.latestMedia = []
        //   this.tweets = res.data
        //   this.tweetMedia = {}
        //   this.getTweetSummary()
        // }

        this.showingDropdown = false
      } catch (e) {
        this.loading = false
        this.summaryLoading = false

        if (this.summary.length) {
          this.tweetMedia = []
          this.summaries.push({
            summary: 'No results found. Try a different request',
            clips: [],
            media: [],
          })

          this.showingArticles = false
          this.secondaryLoaderAlt = false
        } else {
          this.showingArticles = false
          this.latestArticles = []
          this.latestMedia = []
          this.secondaryLoaderAlt = false
        }
      } finally {
        this.refreshUser()
        this.loading = false
      }
    },
    async getPosts(saved = false) {
      this.summary = null
      this.loading = true
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        await Comms.api
          .getPosts({
            hashtag: this.newSearch,
            user_id: this.user.id,
            date_from: this.dateStart,
            date_to: this.dateEnd,
          })
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }

            if (response.posts.length) {
              this.posts = response.posts
                .slice()
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

              this.posts.forEach((post) => {
                post.currentIndex = 0
              })

              this.getPostsSummary()
            }
            this.showingDropdown = false
          })
      } catch (e) {
        console.log(e)
        this.$toast(`${e.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.clearNewSearch()
      } finally {
        this.loading = false
      }
    },
    // prepareTweetSummary(tweets) {

    //   let tweetList = []
    //   for (let i = 0; i < tweets.length; i++) {
    //     if (tweets[i].type === 'twitter') {
    //       tweetList.push({
    //         citationIndex: i,
    //         type: tweets[i].type,
    //         name: tweets[i].user.name,
    //         tweet: tweets[i].text,
    //         followerCount: tweets[i].user.public_metrics.followers_count,
    //         date: tweets[i].created_at,
    //         link: `https://twitter.com/${tweets[i].username}/status/${tweets[i].id}`,
    //       })
    //     } else if (tweets[i].type === 'youtube') {
    //       tweetList.push({
    //         citationIndex: i,
    //         type: tweets[i].type,
    //         name: tweets[i].author,
    //         description: tweets[i].text ? tweets[i].text : tweets[i].title ? tweets[i].title : '',
    //         date: tweets[i].created_at,
    //         link: tweets[i].url,
    //       })
    //     } else {
    //       tweetList.push({
    //         citationIndex: i,
    //         type: tweets[i].type,
    //         name: tweets[i].author,
    //         description: tweets[i].text ? tweets[i].text : '',
    //         date: tweets[i].created_at,
    //         link: tweets[i].url,
    //         interactions: tweets[i].stats,
    //       })
    //     }
    //   }

    //   return tweetList
    // },

    prepareTweetSummary(tweets) {
      let tweetList = []

      for (let i = 0; i < tweets.length; i++) {
        if ('type' in tweets[i]) {
          if (tweets[i].type === 'twitter') {
            tweetList.push({
              citationIndex: i,
              type: tweets[i].type,
              name: tweets[i].user.name,
              tweet: tweets[i].text,
              followerCount: tweets[i].user.public_metrics.followers_count,
              date: tweets[i].created_at,
              link: `https://twitter.com/${tweets[i].username}/status/${tweets[i].id}`,
            })
          } else if (tweets[i].type === 'youtube') {
            tweetList.push({
              citationIndex: i,
              type: tweets[i].type,
              name: tweets[i].author,
              description: tweets[i].text ? tweets[i].text : tweets[i].title ? tweets[i].title : '',
              date: tweets[i].created_at,
              link: tweets[i].url,
            })
          } else {
            tweetList.push({
              citationIndex: i,
              type: tweets[i].type,
              name: tweets[i].author,
              description: tweets[i].text ? tweets[i].text : '',
              date: tweets[i].created_at,
              link: tweets[i].url,
              interactions: tweets[i].stats,
            })
          }
        }
        // Objects without 'type' property are not included
      }

      return tweetList
    },

    prepareIgSummary(posts) {
      let postList = []
      for (let i = 0; i < posts.length; i++) {
        postList.push(
          'Date: ' +
            posts[i].timestamp +
            'likes: ' +
            posts[i].like_count +
            'Comments: ' +
            posts[i].comments_count +
            ' Caption:' +
            posts[i].caption,
          // 'likes: ' +
          // posts[i].likes_count +
        )
      }
      return postList
    },
    // getArticleDescriptions(articles) {
    //   return articles.map(
    //     (a) =>
    //       `Content:${a.description} Date:${a.publish_date}, Source:${a.source.name}, Author:${a.author}, Link: ${a.link}`,
    //   )
    // },
    getArticleDescriptions(articles) {
      if (this.mainView === 'omni') {
        return articles
          .map((a, index) => {
            // Only process articles that DON'T have 'type' or 'snippet'
            if (!('type' in a) && !('snippet' in a)) {
              return {
                citationIndex: index, // Based on the original list
                content: `Content: ${a.description}`,
                date: `Date: ${a.publish_date}`,
                source: `Source: ${a.source.name}`,
                author: `Author: ${a.author}`,
                link: `Link: ${a.link}`,
                shares: `Total shares: ${a.shares ? a.shares : 0}`,
              }
            }
            return null
          })
          .filter(Boolean)
      } else {
        return articles.map((a, index) => ({
          citationIndex: index,
          content: `Content: ${a.description}`,
          date: `Date: ${a.publish_date}`,
          source: `Source: ${a.source.name}`,
          author: `Author: ${a.author}`,
          link: `Link: ${a.link}`,
          shares: `Total shares: ${a.shares ? a.shares : 0}`,
        }))
      }
    },
    async regenerateOmniSummary(clips, instructions) {
      let news = this.getArticleDescriptions(clips)
      let tweets = this.prepareTweetSummary(clips)
      let google = clips.filter((clip) => clip.hasOwnProperty('snippet'))

      try {
        const res = await Comms.api.omniSummary({
          search: instructions,
          original: this.summaries.length
            ? this.summaries[this.summaries.length - 1].summary
            : this.summary,
          clips: news,
          social_data: tweets,
          web: google,
          project: this.selectedOrg,
          follow_up: true,
        })

        if (res.summary.toLowerCase().includes('new search term')) {
          this.newSearch = this.extractTerm(res.summary)
          this.secondaryLoader = false
          this.secondaryLoaderAlt = true
          this.generateNewSearch(null, false)
          if (this.searchSaved) {
            this.updateSearch()
          }
        } else {
          this.summaries.push({
            summary: res.summary
              .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
              .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, ''),
            clips: this.latestArticles.length ? this.latestArticles : [],
          })
          this.secondaryLoader = false
          this.secondaryLoaderAlt = false

          if (this.searchSaved) {
            this.updateSearch()
          }

          this.$nextTick(() => {
            this.scrollToSummariesTop()
          })

          setTimeout(() => {
            this.altCitationsMounted = true
          }, 5000)
        }

        this.secondaryLoader = false
      } catch (e) {
        console.log(e)
        this.secondaryLoaderAlt = false

        this.summaries.push({
          summary: 'No results found. Try a different request',
          clips: [],
        })
      } finally {
      }
    },
    async regenerateTwitterSummary(clips, instructions) {
      try {
        const res = await Comms.api.getTweetSummary({
          query: this.newSearch,
          instructions: instructions,
          previous: this.summary,
          tweets: clips,
          project: this.selectedOrg,
          followUp: true,
        })

        if (res.summary.toLowerCase().includes('new search term')) {
          this.newSearch = this.extractTerm(res.summary)
          this.secondaryLoader = false
          this.secondaryLoaderAlt = true
          this.generateNewSearch(null, false)
          if (this.searchSaved) {
            this.updateSearch()
          }
        } else {
          this.summaries.push({
            summary: res.summary
              .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
              .replace(/(?:<strong>\s*Email:\s*<\/strong>|email:\s*)([^<"]+)/i, ''),
            clips: this.latestArticles.length ? this.latestArticles : [],
            media: this.latestMedia ? this.latestMedia : [],
          })
          this.secondaryLoader = false
          this.secondaryLoaderAlt = false

          if (this.searchSaved) {
            this.updateSearch()
          }

          this.$nextTick(() => {
            this.scrollToSummariesTop()
          })

          setTimeout(() => {
            this.altCitationsMounted = true
          }, 5000)
        }

        this.secondaryLoader = false
      } catch (e) {
        console.log(e)
        this.secondaryLoaderAlt = false

        this.summaries.push({
          summary: 'No results found. Try a different request',
          clips: [],
          media: [],
        })
      } finally {
      }
    },
    async getTweetSummary(instructions = '') {
      this.citationsMounted = false

      let tweets = this.prepareTweetSummary(
        this.latestArticles.length ? this.latestArticles : this.tweets,
      )
      this.preparedTweets = tweets
      if (!this.summary) {
        this.summaryLoading = true
      }

      // this.summary = ''
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        const res = await Comms.api.getTweetSummary({
          tweets: tweets,
          search: this.newSearch,
          instructions: this.newTemplate ? this.newTemplate : this.newSearch,
          company: this.selectedOrg,
        })

        if (this.shouldCancel) {
          return this.stopLoading()
        }

        if (this.summary) {
          this.summaries.push({
            summary: res.summary
              .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
              .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>'),
            clips: this.latestArticles.length ? this.latestArticles : [],
            media: this.latestMedia ? this.latestMedia : [],
          })
          this.secondaryLoader = false
          this.secondaryLoaderAlt = false
          this.$nextTick(() => {
            this.scrollToSummariesTop()
          })
          setTimeout(() => {
            this.altCitationsMounted = true
          }, 5000)
        } else {
          this.summary = res.summary
            .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')

          this.$nextTick(() => {
            this.scrollToTop()
          })
        }

        this.refreshUser()
      } catch (e) {
        console.log('Error in getTweetSummary', e)
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summaryLoading = false
      }
    },
    async getPostsSummary(instructions = '') {
      let posts = this.prepareIgSummary(this.posts)
      this.summaryLoading = true
      this.summary = ''
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        await Comms.api
          .getPostsSummary({
            posts: posts,
            instructions: this.newTemplate,
          })
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            this.summary = response.summary
            if (this.searchSaved) {
              this.updateSearch()
            }
            this.refreshUser()
          })
      } catch (e) {
        console.log('Error in getTweetSummary', e)
        this.$toast(`Error: ${e}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summarizing = true
        this.summaryLoading = false
        this.showSummaryMenu = false
      }
    },
    async getChatSummary(event, clips, instructions = '') {
      if (event.shiftKey) {
        return
      }

      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }

      if (!this.summary) {
        this.newSearch = this.newTemplate
        if (this.mainView !== 'news' || this.mainView !== 'trending') {
          this.generateNewSearch(null, false)
        } else {
          this.regenerateSummary()
        }
        return
      }

      this.noResultsString = null
      this.followUps.push(this.newTemplate)
      this.newTemplate = ''
      this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
      this.scrollToBottom()
      this.secondaryLoader = true
      this.chatSummaryLoading = true
      this.showingPromptDropdown = false
      this.showSummaryMenu = false
      this.altCitationsMounted = false
      try {
        if (this.mainView === 'news' || this.mainView === 'trending') {
          await this.getSummary(
            clips,
            instructions,
            this.summaries.length
              ? this.summaries[this.summaries.length - 1].summary
              : this.summary,
            false,
            null,
            true,
          )
        } else if (this.mainView === 'social') {
          await this.regenerateTwitterSummary(clips, instructions, true)
        } else if (this.mainView === 'web') {
          this.regenerateGoogleSearch(clips, instructions)
        } else if (this.mainView === 'discover') {
          this.discoverJournalists(false)
        } else if (this.mainView === 'omni') {
          let omniClips = []
          omniClips = this.latestArticles.length ? this.latestArticles : this.omniResults
          await this.regenerateOmniSummary(omniClips, instructions, true)
        }
      } catch (e) {
        console.log('error in getChatSummary', e)
      }
      this.chatSummaryLoading = false
    },

    async regeneratePitch(event) {
      if (event.shiftKey) {
        return
      }
      this.secondaryLoader = true
      this.followUps.push(this.newTemplate)
      this.newTemplate = ''
      this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
      this.scrollToBottom()

      try {
        const res = await Comms.api.regeneratePitch({
          pitch: this.summaries.length ? this.summaries[this.summaries.length - 1] : this.summary,
          instructions: this.followUps[this.followUps.length - 1],
          style: this.writingStyle,
          details: this.selectedOrg,
        })

        this.summaries.push({
          summary: res.pitch,
          clips: [],
        })

        if (this.searchSaved) {
          this.updateSearch()
        }

        this.$nextTick(() => {
          this.scrollToSummariesTop()
        })
      } catch (e) {
        console.log('ERROR CREATING PITCH::', e)
      } finally {
        this.refreshUser()
        this.secondaryLoader = false
      }
    },

    async regenerateSummary() {
      this.loading = true
      try {
        const res = await Comms.api.getSummary({
          clips: [],
          search: this.newSearch,
          instructions: this.newSearch,
          company: this.selectedOrg,
          previous: this.noResultsString,
          followUp: true,
          trending: this.mainView === 'trending' ? true : false,
        })

        if (res.summary.toLowerCase().includes('new search term')) {
          this.newSearch = this.extractTerm(res.summary)
          this.generateNewSearch(null, false)
        } else {
          this.summary = res.summary
            .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
        }
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    // async getTrendingSummary(
    //   clips,
    //   instructions = '',
    //   previous,
    //   twitter = false,
    //   chatSummary = null,
    //   followUp = false,
    // ) {
    //   this.citationsMounted = false

    //   allClips = this.getArticleDescriptions(
    //      clips,
    //     )

    //   if (!this.summary) {
    //     this.summaryLoading = true
    //   }

    //   let openAiDown = false

    //   try {
    //     await Comms.api
    //       .getTrendingSummary({
    //         clips: allClips,
    //         search: this.newSearch,
    //         instructions: instructions,
    //         company: this.selectedOrg,
    //         previous: previous ? previous : null,
    //         followUp: followUp,
    //       })
    //       .then((response) => {
    //         if (this.shouldCancel) {
    //           return this.stopLoading()
    //         }
    //         if (this.searchSaved) {
    //           this.updateSearch()
    //         }
    //         this.originalSummary = response.summary
    //         if (this.summary) {
    //           if (response.summary.toLowerCase().includes('new search term')) {
    //             this.newSearch = this.extractTerm(response.summary)
    //             this.secondaryLoader = false
    //             this.secondaryLoaderAlt = true
    //             this.generateNewSearch(null, false)
    //           } else {
    //             this.summaries.push({
    //               summary: response.summary
    //                 .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
    //                 .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>'),
    //               clips: this.latestArticles.length ? this.latestArticles : [],
    //             })
    //             this.secondaryLoader = false
    //             this.secondaryLoaderAlt = false
    //             setTimeout(() => {
    //               this.altCitationsMounted = true
    //             }, 5000)
    //           }
    //         } else {
    //           this.summary = response.summary
    //             .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
    //             .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
    //         }
    //       })
    //   } catch (e) {
    //     console.log('Error in getSummary', e)
    //     this.laoding = false
    //     this.summaryLoading = false
    //     this.secondaryLoader = false
    //     this.secondaryLoaderAlt = false
    //     if (
    //       e.data &&
    //       e.data.summary === "Unknown exception: 'NoneType' object is not subscriptable"
    //     ) {
    //       this.$toast('OpenAI is down, please try again later.', {
    //         timeout: 2000,
    //         position: 'top-left',
    //         type: 'error',
    //         toastClassName: 'custom',
    //         bodyClassName: ['custom'],
    //       })
    //       openAiDown = true
    //     } else {
    //       this.$toast('Something went wrong, please try again.', {
    //         timeout: 2000,
    //         position: 'top-left',
    //         type: 'error',
    //         toastClassName: 'custom',
    //         bodyClassName: ['custom'],
    //       })
    //     }
    //   } finally {
    //     if (this.summaries.length && !this.secondaryLoader && !this.secondaryLoaderAlt) {
    //       this.scrollToSummariesTop()
    //     } else {
    //       this.scrollToBottom()
    //     }

    //     if (openAiDown) {
    //       // this.changeSearch({ search: null, template: null })
    //       this.resetSearch()
    //       this.abortFunctions()
    //       return this.stopLoading()
    //     }
    //     const newAbortControllers = { ...this.$store.state.abortControllers }
    //     delete newAbortControllers.getClips
    //     this.$store.dispatch('updateAbortController', newAbortControllers)
    //     this.summarizing = true
    //     this.summaryLoading = false
    //     if (chatSummary) {
    //       this.newTemplate = ''
    //     }
    //     if (this.chatting) {
    //       this.chatting = false
    //       this.changeSearch({ search: this.booleanString, template: this.newTemplate })
    //     }
    //     this.refreshUser()
    //   }
    // },
    async getSummary(
      clips,
      instructions = '',
      previous,
      twitter = false,
      chatSummary = null,
      followUp = false,
    ) {
      this.citationsMounted = false
      // this.altCitationsMounted = false
      let allClips

      if (!twitter) {
        allClips = this.getArticleDescriptions(
          this.latestArticles.length ? this.latestArticles : clips,
        )
      } else {
        allClips = clips
      }

      if (!this.summary) {
        this.summaryLoading = true
      }

      let openAiDown = false
      // this.summary = ''
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        this.$store.dispatch('updateAbortController', {
          ...this.$store.state.abortControllers,
          getSummary: { name: 'getSummary', controller: new AbortController() },
        })
        await Comms.api
          .getSummary(
            {
              clips: allClips,
              search: this.newSearch,
              instructions: instructions,
              company: this.selectedOrg,
              previous: previous ? previous : null,
              followUp: followUp,
              trending: this.mainView === 'trending' ? true : false,
            },
            this.controllers.getSummary.controller.signal,
          )
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            if (this.searchSaved) {
              this.updateSearch()
            }
            this.originalSummary = response.summary
            if (this.summary) {
              if (response.summary.toLowerCase().includes('new search term')) {
                this.newSearch = this.extractTerm(response.summary)
                this.secondaryLoader = false
                this.secondaryLoaderAlt = true
                this.generateNewSearch(null, false)
              } else {
                this.summaries.push({
                  summary: response.summary
                    .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
                    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>'),
                  clips: this.latestArticles.length ? this.latestArticles : [],
                })
                this.secondaryLoader = false
                this.secondaryLoaderAlt = false
                setTimeout(() => {
                  this.altCitationsMounted = true
                }, 5000)
              }
            } else {
              this.summary = response.summary
                .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
                .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
            }
          })
      } catch (e) {
        console.log('Error in getSummary', e)
        this.loading = false
        this.summaryLoading = false
        this.secondaryLoader = false
        this.secondaryLoaderAlt = false
        if (
          e.data &&
          e.data.summary === "Unknown exception: 'NoneType' object is not subscriptable"
        ) {
          this.$toast('OpenAI is down, please try again later.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          openAiDown = true
        } else {
          this.$toast('Something went wrong, please try again.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        if (this.summaries.length && !this.secondaryLoader && !this.secondaryLoaderAlt) {
          this.scrollToSummariesTop()
        } else {
          this.scrollToBottom()
        }

        if (openAiDown) {
          // this.changeSearch({ search: null, template: null })
          this.resetSearch()
          this.abortFunctions()
          return this.stopLoading()
        }
        const newAbortControllers = { ...this.$store.state.abortControllers }
        delete newAbortControllers.getClips
        this.$store.dispatch('updateAbortController', newAbortControllers)
        this.summarizing = true
        this.summaryLoading = false
        if (chatSummary) {
          this.newTemplate = ''
        }
        if (this.chatting) {
          this.chatting = false
          this.changeSearch({ search: this.booleanString, template: this.newTemplate })
        }
        this.refreshUser()
      }
    },
    async regenerateArticleSummary(url, summary, instructions) {
      let selectedClip = this.addedArticles.length
        ? this.addedArticles.filter((art) => art.link === url)[0]
        : this.filteredArticles.filter((art) => art.link === url)[0]

      this.articleSummaryLoading = true
      this.loadingUrl = url

      try {
        const response = await Comms.api.regenerateArticleSummary({
          url,
          summary: summary,
          instructions: instructions,
        })
        selectedClip['summary'] = response.summary
        if (!this.addedArticles.length) {
          this.filteredArticles = this.filteredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.filteredArticles.unshift(selectedClip)
        } else {
          this.addedArticles = this.addedArticles = this.addedArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.addedArticles.unshift(selectedClip)
        }

        this.refreshUser()
        this.scrollToTopDivider()
      } catch (e) {
        console.log(e)
      } finally {
        this.showArticleRegenerate = false
        this.articleSummaryLoading = false
        this.loadingUrl = null
      }
    },
    extractTerm(input) {
      const match = input.match(/\[(.*?)\]/)
      return match ? match[1] : ''
    },
    selectArticle(article) {
      this.$store.dispatch('updateSelectedArticle', article)
    },
    goToArticle(link) {
      this.addLinkInteraction(link)
      window.open(link, '_blank')
    },
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
  },
  computed: {
    reportCredits() {
      return !!this.$store.state.user.organizationRef.metaData
        ? this.$store.state.user.organizationRef.metaData.reportCredits
        : 0
    },
    isViewOnly() {
      return this.$store.state.viewOnly
    },
    allThreads() {
      return this.$store.state.allThreads
    },
    hasGoogleIntegration() {
      return !!this.$store.state.user.hasGoogleIntegration
    },
    hasMicrosoftIntegration() {
      return !!this.$store.state.user.hasMicrosoftIntegration
    },
    sidebarArticles() {
      return this.alternateAricles.length ? this.alternateAricles : this.filteredArticles
    },
    sidebarArticlesWeb() {
      return this.alternateAricles.length ? this.alternateAricles : this.filteredResults
    },
    sidebarArticlesOmni() {
      return this.alternateAricles.length ? this.alternateAricles : this.omniResults
    },
    sidebarArticlesSocial() {
      return this.alternateAricles.length ? this.alternateAricles : this.tweets
    },
    filteredChannels() {
      if (this.userChannelOpts) {
        return this.userChannelOpts.channels.filter((channel) =>
          channel.name.toLowerCase().includes(this.searchChannelText.toLowerCase()),
        )
      } else {
        return ['Nothing here...']
      }
    },
    userWritingStyles() {
      if (this.personalStyles) {
        return this.allWritingStyles.filter((style) => style.user === this.user.id)
      } else {
        return this.allWritingStyles
      }
    },
    mailtoLink() {
      return `mailto:${this.supportEmail}`
    },
    upgradeLink() {
      return 'https://managr.ai/contact'
    },
    onboardingLink() {
      return 'https://www.loom.com/share/c5aaab7f524c4cf4a8c68d478541c354?sid=8ecaa01e-7fb6-4172-8f6f-527c62616bc7'
    },
    placeHolderText() {
      let text = ''
      if (this.mainView === 'social' && !this.hasTwitterIntegration) {
        text = 'Connect Twitter...'
      } else if (this.mainView === 'news') {
        text = 'Search news...'
      } else if (this.mainView === 'social') {
        text = 'Search social media...'
      } else if (this.mainView === 'web') {
        text = 'Search the web...'
      } else if (this.mainView === 'write') {
        text = 'Message ManagrAI...'
      } else if (this.mainView === 'discover') {
        text = 'Find relevant journalists...'
      }

      return text
    },
    minDate() {
      const currentDate = new Date()
      const priorDate = new Date(currentDate.getTime() - 30 * 24 * 60 * 60 * 1000)
      return priorDate.toISOString().slice(0, 10)
    },
    minDateSocial() {
      const currentDate = new Date()
      const priorDate = new Date(currentDate.getTime() - 7 * 24 * 60 * 60 * 1000)
      return priorDate.toISOString().slice(0, 10)
    },
    articlesFiltered: {
      get() {
        let articles = this.filteredArticles.filter((article) => {
          const searchText = this.searchArticleText.toLowerCase()

          const searchConditions = [
            article.source &&
              article.source.name &&
              article.source.name.toLowerCase().includes(searchText),
            article.title && article.title.toLowerCase().includes(searchText),
            article.description && article.description.toLowerCase().includes(searchText),
            // article.author && article.author.toLowerCase().includes(searchText),
          ]

          const filterConditions = []

          return (
            searchConditions.some((condition) => condition) &&
            filterConditions.every((condition) => condition)
          )
        })

        return articles
      },
    },
    // omniResults() {
    //   let articles = this.omniNews.concat(this.omniSocial, this.omniWeb)

    //   return articles
    // },
    filteredResults: {
      get() {
        let articles = this.googleResults.filter((article) => {
          const searchText = this.searchResultText.toLowerCase()

          const searchConditions = [
            article.source && article.source.toLowerCase().includes(searchText),
            article.title && article.title.toLowerCase().includes(searchText),
            article.snippet && article.snippet.toLowerCase().includes(searchText),
            article.author && article.author.toLowerCase().includes(searchText),
          ]

          const filterConditions = []

          return (
            searchConditions.some((condition) => condition) &&
            filterConditions.every((condition) => condition)
          )
        })

        return articles
      },
    },
    filteredTweets: {
      get() {
        let tweetsFiltered = this.tweets
        // let tweetsFiltered = this.tweets.filter((tweet) => {
        //   const searchText = this.searchTweetText.toLowerCase()

        //   const searchConditions = [
        //     // tweet.user.public_metrics.followers_count.includes(searchText),
        //     tweet.user.name && tweet.user.name.toLowerCase().includes(searchText),
        //     tweet.user.username && tweet.user.username.toLowerCase().includes(searchText),
        //     tweet.text && tweet.text.toLowerCase().includes(searchText),
        //   ]

        //   const filterConditions = []

        //   return (
        //     searchConditions.some((condition) => condition) &&
        //     filterConditions.every((condition) => condition)
        //   )
        // })

        return tweetsFiltered
      },
      dependsOn: ['tweets', 'searchTwitterText'],
    },

    usedHashtags() {
      if (this.user.instagramAccountRef && this.user.instagramAccountRef.hashtagList) {
        return this.user.instagramAccountRef.hashtagList
      } else {
        return []
      }
    },
    hasTwitterIntegration() {
      return !!this.$store.state.user.hasTwitterIntegration
    },
    hasIgIntegration() {
      return !!this.$store.state.user.hasInstagramIntegration
    },
    clipTitles() {
      if (Object.keys(this.$store.state.categories).length) {
        return this.allCategoryClips
          ? this.allCategoryClips.map((clip) => (clip.title ? clip.title : clip.id))
          : []
      } else {
        return this.addedClips
          ? this.addedClips.map((clip) => (clip.title ? clip.title : clip.id))
          : []
      }
    },
    isMobile() {
      return window.innerWidth <= 600
    },
    controllers() {
      return this.$store.state.abortControllers
    },
    allCategoryClips() {
      const cats = this.$store.state.categories
      if (Object.keys(cats).length) {
        let addedClips = []
        for (let key in cats) {
          addedClips = [...addedClips, ...cats[key]]
        }
        return addedClips
      } else return this.addedClips
    },
    messages() {
      return this.$store.state.messages
    },
    userName() {
      return this.$store.state.user.firstName
    },
    user() {
      return this.$store.state.user
    },
    currentSearch() {
      return this.$store.state.currentSearch
    },
    filteredSuggestions() {
      if (!this.newTemplate) return this.searchSuggestions
      return this.searchSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newTemplate.toLowerCase()),
      )
    },
    filteredPromptSuggestions() {
      if (!this.newTemplate) return this.promptSuggestions
      return this.promptSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newTemplate.toLowerCase()),
      )
    },
    isPaid() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user && this.$store.state.user.organizationRef.isPaid
    },
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
    // searchSaved() {
    //   if (
    //     this.newSearch &&
    //     this.currentSearch &&
    //     this.currentSearch.input_text === this.newSearch
    //   ) {
    //     return true
    //   } else if (this.savedSearch && this.newSearch === this.savedSearch.input_text) {
    //     return true
    //   } else {
    //     return false
    //   }
    // },
    fromNav() {
      return this.$store.state.fromNav
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto' // Reset the height
          el.style.height = el.scrollHeight + 'px' // Set it to the scroll height
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', function () {
          el.value = '' // Clear the textarea content
          el.style.height = 'auto' // Reset the height
        })

        adjustTextareaHeight()
      },
    },

    clickOutsideMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
    clickOutsidePromptMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hidePromptDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },

    typed: {
      bind(el, binding) {
        let text = binding.value
        let index = 0
        el.innerHTML = ''

        function type() {
          if (index < text.length) {
            el.innerHTML += text.charAt(index)
            index++
            setTimeout(type, 12)
          }
        }

        type()
      },
      // update(el, binding) {
      //   let text = binding.value
      //   let index = 0
      //   el.innerHTML = ''

      //   function type() {
      //     if (index < text.length) {
      //       el.innerHTML += text.charAt(index)
      //       index++
      //       setTimeout(type, 20)
      //     }
      //   }

      //   type()
      // },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.s-tooltip {
  visibility: hidden;
  width: 100px;
  background-color: $dark-black-blue;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
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
  width: 120px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 100%;
  right: 130%;
  margin-top: -24px;
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

// .menu-wrapper {
//   position: relative;
//   display: inline-block;

//   &:hover {
//     background-color: red;
//     .help-menu {
//       visibility: visible !important;
//       opacity: 1;
//     }
//   }
// }

::v-deep .ql-snow.ql-toolbar button {
  background: $soft-gray;
  border-radius: 4px;
  margin: 0 4px 4px 0;
}

::v-deep .pre-text span {
  // border-bottom: 1px solid rgba(0, 0, 0, 0.128);
  // padding-bottom: 2px;
  display: inline-block;
  margin-top: -40px;
  cursor: pointer;
}

::v-deep .citation-text {
  .author {
    display: inline-block;
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin-right: 8px;
    color: $base-gray;
    border-radius: 16px;
    padding: 5px 6px;
    background-color: $soft-gray;
    cursor: pointer;
    font-family: $base-font-family;
    // p {
    //   overflow: hidden;
    //   white-space: nowrap;
    //   text-overflow: ellipsis;
    //   font-size: 12px !important;
    // }

    &:hover {
      background-color: $soft-gray;
    }

    strong {
      font-size: 13px !important;
    }
  }

  .row {
    display: inline-block;
    vertical-align: middle !important; /* Aligns inline-block elements vertically */
    white-space: nowrap;
  }

  .row-even {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    // justify-content: space-between;
  }

  .row > * {
    display: inline-block;
    vertical-align: middle; /* Ensures children align centrally */
  }

  .inline-svg {
    height: 10px !important;
    filter: invert(30%) !important;
  }

  .inline-link {
    font-family: $base-font-family;
    display: inline-block;
    font-size: 14px;
    color: $dark-gray-blue;
    text-decoration: none;
    padding-bottom: 2px;
  }

  .inline-link:hover {
    text-decoration: underline;
    color: $lite-blue;
  }

  sup {
    line-height: 1;
    display: inline;
    vertical-align: super;
  }

  .citation-link-alt {
    padding: 4px !important;

    img {
      height: 9px !important;
      filter: invert(45%) sepia(52%) saturate(1248%) hue-rotate(196deg) brightness(97%)
        contrast(90%) !important;
    }
  }
  .citation-link {
    padding: 4px 6px 4.5px 5px;
    margin: 0 1px;
    font-size: 9px;
    border: 0.5px solid $lite-blue;
    background-color: white;
    border-radius: 100%;
    text-decoration: none;
    cursor: pointer;
    font-family: $base-font-family;
    font-weight: 900;
    color: $lite-blue;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .citation-link:hover {
    text-decoration: underline;
    background-color: $lite-blue;
    color: white;
    opacity: 1;

    img {
      filter: invert(100%) !important;
    }
  }

  .citation-tooltip {
    visibility: hidden;
    width: 254px;
    background-color: #fff;
    color: #333;
    text-align: left;
    border-radius: 4px;
    padding: 10px;
    position: absolute;
    z-index: 100000;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(0, 0, 0, 0.128);
    font-size: 13px;
    line-height: 1.4;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    strong {
      font-size: 12px !important;
    }
    img {
      width: 40px !important;
      height: 40px !important;
      margin-left: 8px;
      vertical-align: middle;
      border-radius: 4px;
    }
  }

  .c-blue {
    color: $lite-blue;
    cursor: pointer;

    &:hover {
      text-decoration: underline;
    }
  }

  .c-elip {
    max-height: 40px;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .span-row {
    display: flex;
    flex-direction: row;
    align-items: center;

    img {
      height: 14px !important;
      width: 14px !important;
      margin-right: 8px;
      margin-left: 0 !important;
    }
  }

  .c-elip-small {
    max-height: 40px;
    max-width: 180px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    cursor: pointer !important;

    &:hover {
      text-decoration: underline;
    }
  }

  .citation-tooltip.show {
    visibility: visible;
    opacity: 1;
    pointer-events: auto;
  }

  .citation-wrapper,
  .citation-wrapper-alt {
    position: relative;
    display: inline-block;
  }

  // .citation-wrapper:hover .citation-tooltip {
  //   visibility: visible;
  //   opacity: 1;
  // }

  // a {
  //   color: $grape;
  //   border-bottom: 1px solid $grape;
  //   font-family: $base-font-family;
  //   text-decoration: none;
  //   padding-bottom: 2px;

  //   &:hover {
  //     opacity: 0.7;
  //   }
  // }

  strong,
  h1,
  h2,
  h3 {
    font-family: $base-font-family;
  }

  strong,
  h3 {
    font-size: 16px !important;
  }

  h2 {
    font-size: 20px !important;
  }

  .primary-button {
    @include dark-blue-button();
    padding: 8px 12px;
    border: none;
    border-radius: 16px;
    margin: 12px 0 0 0;
  }

  p {
    margin: 0;
  }
}

::v-deep .ql-toolbar.ql-snow {
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 4px;
  padding: 0;
  min-width: 500px;
}

::v-deep .ql-container {
  border: none;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  padding: 8px 0 0 0;
  margin-left: -8px;
}

::v-deep .alternate {
  strong {
    font-family: $base-font-family;
    cursor: pointer;
  }
}

::v-deep .ql-editor {
  font-family: $thin-font-family;
  font-size: 14px;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.5s ease-in;
}
.slide-up-enter,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.redbg {
  background: $light-coral !important;
  border: 1px solid $coral !important;
}
.greenbg {
  background: $white-green !important;
}

.base-img {
  img {
    filter: invert(30%);
    margin-right: 4px;
  }
  color: $dark-black-blue !important;
}

.red-img {
  img {
    filter: invert(46%) sepia(43%) saturate(800%) hue-rotate(308deg) brightness(104%) contrast(97%);
    margin-right: 4px;
  }
  color: $coral !important;
}

.green-img {
  img {
    filter: invert(65%) sepia(5%) saturate(4090%) hue-rotate(101deg) brightness(95%) contrast(88%);
    margin-right: 4px;
  }
  color: $dark-green !important;
}

.abs-placed {
  position: absolute;
  right: 4px;
  top: 18px;

  p {
    padding: 0;
    margin: 0 4px 0 0;
  }
}

.red-bg {
  background-color: $coral;
  padding: 4px;
  border-radius: 4px;
}

.coraltext {
  color: $coral !important;
}

.greenText {
  color: $dark-green !important;
}

.secondary-button-white {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  padding: 8px 12px;
  background-color: white;
  color: $dark-black-blue !important;
  font-family: $base-font-family !important;

  &:hover {
    background-color: rgba(0, 0, 0, 0.005);
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
    background-color: $soft-gray;
    transform: none !important;
    box-shadow: none;
  }
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

.primary-input-underline {
  width: 100%;
  margin: 1rem 0;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.135);
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 13px;
  padding: 4px 20px 16px 18px;
  outline: none;

  @media only screen and (max-width: 600px) {
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
  }
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

.text-editor {
  height: 35vh;
  width: 100%;
  border-radius: 8px;
  // background-color: red;

  @media only screen and (max-width: 600px) {
    height: 140px;
  }
}

.link {
  border-bottom: 1px solid $dark-black-blue;
  padding-bottom: 2px;
  cursor: pointer;
}

.dropdownBorder {
  color: $dark-black-blue !important;
  border-radius: 16px;
  // background-color: white;
  font-size: 14px !important;
  // border: 0.5px solid $dark-black-blue;
  padding: 7.5px 8px !important;

  span {
    font-family: $base-font-family !important;
    margin-left: 4px;
  }

  &:hover {
    background-color: $dark-black-blue;
    color: white !important;
    img {
      filter: invert(100%);
    }
    // border: 0.5px solid rgba(0, 0, 0, 0.1);
  }
}

.date-dropdown {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 1rem;
  position: absolute;
  bottom: 64px;
  right: 0;
  background: white;

  input {
    margin-top: 1rem;
  }
}

.nav-text {
  font-weight: 400;
  font-family: $thin-font-family;
  color: #6b6b6b;
  font-size: 13px;
  padding: 6px 0;
  img {
    margin-left: 8px;
  }
}

.content-dropdown {
  width: 260px;
  position: absolute;
  top: 150px;
  left: auto;
  font-size: 13px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 1000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    padding: 8px 16px;
    color: #7c7b7b;
    cursor: pointer;
    width: 245px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
  }
}

.search-dropdown {
  width: 260px;
  position: absolute;
  bottom: 40px;
  right: -8px;
  font-size: 13px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 1000;
  border: 1px solid rgba(0, 0, 0, 0.135);

  p {
    padding: 8px 16px;
    color: #7c7b7b;
    cursor: pointer;
    width: 260px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
    background-color: $soft-gray;
  }
}

.mobile-text-hide {
  @media only screen and (max-width: 600px) {
    display: none;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    // overflow: hidden;
    // text-overflow: ellipsis;
    // white-space: nowrap;
    display: none;
  }
  @media only screen and (min-width: 1025px) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.dropdown-small {
  position: absolute;
  top: 96px;
  width: 340px;
  right: 32px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  z-index: 10;
  padding: 16px 16px 0 16px;
  border-radius: 6px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

  label {
    font-family: $base-font-family;
  }

  small {
    font-size: 13px;
  }

  &-header {
    padding: 0;
    position: sticky;
    top: 0;
    background-color: white;
    font-size: 18px;
    font-family: $base-font-family;
    font-weight: 200;
  }

  &-section {
    padding: 16px 0;
    display: flex;
    flex-direction: column !important;
    align-items: flex-start;
    justify-content: flex-start;
    gap: 8px;
  }

  &-bb {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }

  div {
    width: 100%;

    button {
      margin-left: auto;
      img {
        margin-right: 8px;
      }
    }
  }

  @media only screen and (max-width: 600px) {
    width: 60vw;
  }
}

.source-dropdown {
  z-index: 1;

  @media only screen and (max-width: 600px) {
    margin-top: 8px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    // width: 32%;
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
    // overflow: hidden;
    // text-overflow: ellipsis;
    // white-space: nowrap;
    // width: 32%;
  }

  p {
    font-size: 14px !important;
  }
  position: relative;
  margin-top: 16px;

  .drop-header {
    padding: 4px 8px 4px 0;
    background-color: $off-white;
    font-size: 14px !important;
    border-radius: 10px;
    display: flex;
    flex-direction: row;
    align-items: center;
    cursor: pointer;

    @media only screen and (max-width: 600px) {
      font-size: 12px !important;
    }

    img {
      margin: 0 4px 0 8px;
      filter: invert(40%);

      @media only screen and (max-width: 600px) {
        // display: none;
      }
    }

    small {
      font-size: 14px;
      margin-left: 4px !important;
      font-family: $base-font-family;
      max-width: 100px;
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
    top: 40px;
    right: 0;
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
    width: 520px;
    max-height: 260px;
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
    flex-direction: column;
    align-items: flex-start;

    @media only screen and (max-width: 600px) {
      left: 0;
      width: 85vw;
    }

    header {
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      font-size: 14px;
      padding: 0 0 12px 8px;
      position: sticky;
      top: 0;

      h4 {
        font-family: $base-font-family;
        margin: 0;
        font-size: 16px;
      }
      p {
        margin: 0;
      }
    }

    footer {
      position: sticky;
      bottom: 0;
      background: white;
      width: 100%;
      padding: 12px 0 8px 0;
    }

    section:last-of-type {
      margin-top: 16px;
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      flex-wrap: wrap;
      justify-content: flex-start;
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
      width: 160px;
      height: 70px;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;

      p {
        font-size: 12px !important;
        font-family: $thin-font-family;
        margin: 0 0 0 0;
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
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

  .drop-options-alt-up {
    width: 450px;
    max-height: 260px;
    position: absolute;
    bottom: 40px;
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
    flex-direction: column;
    align-items: flex-start;

    @media only screen and (max-width: 600px) {
      left: 0;
      width: 85vw;
    }

    header {
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      font-size: 14px;
      padding: 0 0 12px 8px;
      position: sticky;
      top: 0;

      h4 {
        font-family: $base-font-family;
        margin: 0;
        font-size: 16px;
      }
      p {
        margin: 0;
      }
    }

    footer {
      position: sticky;
      bottom: 0;
      background: white;
      width: 100%;
      padding: 12px 0 8px 0;
    }

    section:last-of-type {
      margin-top: 16px;
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      flex-wrap: wrap;
      justify-content: flex-start;
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
      height: 70px;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;

      p {
        font-size: 12px !important;
        font-family: $thin-font-family;
        margin: 0 0 0 0;
        max-width: 130px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
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
    left: -8px;
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
        font-size: 12px !important;
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

.left-mobile {
  @media only screen and (max-width: 600px) {
    left: -88px !important;
  }
}
.left-mobile-l {
  @media only screen and (max-width: 600px) {
    left: -160px !important;
  }
}
.left-mobile-m {
  @media only screen and (max-width: 600px) {
    left: -126px !important;
  }
}

.drop-header-alt {
  padding: 10px;
  width: fit-content;
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

.col {
  display: flex;
  flex-direction: column;
}
.col-start {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}

.blue-button {
  @include dark-blue-button();
  background-color: $dark-black-blue !important;
  color: white !important;
  padding: 8px 12px;
  font-size: 14px;
  border: none;
  margin-left: 0;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  border-radius: 16px;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.white-button-round {
  @include dark-blue-button();
  background-color: white;
  padding: 8px 12px;
  color: $dark-black-blue;
  border: 1px solid $dark-black-blue;
}

.opaque {
  opacity: 0.75;
}

.opaquer {
  opacity: 0.45;
}

.opaquest {
  opacity: 0.3;
}

.img-button {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 12px 32px;
  border-radius: 12px;
  color: $dark-black-blue;
  font-size: 16px;
  img {
    filter: invert(40%);
    margin-right: 8px;
  }
}

.img-button-blueicon {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 12px 32px;
  border-radius: 12px;
  color: $dark-black-blue;
  font-size: 16px;
  img {
    filter: invert(22%) sepia(32%) saturate(554%) hue-rotate(161deg) brightness(99%) contrast(90%);
    margin-right: 8px;
  }
}

.blue-icon {
  filter: invert(22%) sepia(32%) saturate(554%) hue-rotate(161deg) brightness(99%) contrast(90%) !important;
}

.img-button-blue {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 16px;
  img {
    filter: invert(100%);
    margin-right: 8px;
  }
}

.img-button-blue-small {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 14px;
  img {
    filter: invert(1000%);
    margin-right: 8px;
  }

  @media only screen and (max-width: 600px) {
    width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    img {
      display: none;
    }
  }
}

.img-button-white {
  @include dark-blue-button();
  background-color: white;
  color: $dark-black-blue;
  border: 1px solid $dark-black-blue;
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 14px;
  img {
    filter: invert(30%);
    margin-right: 8px;
  }

  @media only screen and (max-width: 600px) {
    width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    img {
      display: none;
    }
  }
}

.icon-button {
  @include dark-blue-button();
  padding: 7px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  img {
    filter: invert(40%);
  }
}

.icon {
  cursor: pointer;
  transition: all 0.5s;
  &:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transform: scale(1.15);
  }
}

.green-button {
  @include dark-blue-button();
  background-color: transparent;
  padding: 0;
  border: none;
  margin-right: 0;
  img {
    filter: invert(40%);
  }

  &:disabled {
    img {
      filter: invert(60%);
    }
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
  left: -40px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 6px;
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

.wrapper .tooltip-right {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 2px;
  color: #fff;
  display: block;
  left: 100%;
  margin-left: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateX(-10px);
  -moz-transform: translateX(-10px);
  -ms-transform: translateX(-10px);
  -o-transform: translateX(-10px);
  transform: translateX(-10px);
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
  width: 160px !important;
  left: -72px !important;
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

.wrapper .tooltip-right:before {
  left: -20px;
  content: ' ';
  display: block;
  height: 20px;
  top: 0;
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

.wrapper .tooltip-right:after {
  border-top: solid transparent 10px;
  border-bottom: solid transparent 10px;
  border-right: solid $dark-black-blue 10px;
  left: -10px;
  content: ' ';
  height: 0;
  top: 60%;
  margin-top: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip,
.wrapper:hover .tooltip-wide,
.wrapper:hover .tooltip-below,
.wrapper:hover .tooltip-right {
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
.lt38 .wrapper .tooltip-below,
.lt38 .wrapper .tooltip-right {
  display: none;
}

.lte8 .wrapper:hover .tooltip,
.lte8 .wrapper:hover .tooltip-wide,
.lte8 .wrapper:hover .tooltip-below,
.lte8 .wrapper:hover .tooltip-right {
  display: block;
}

.sub-text {
  margin: 0;
  font-size: 18px;
}

.article-copy-container {
  height: 20px;
  margin-top: 0.5rem;
}

.author {
  max-width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin: 0 8px 0 0 !important;
  color: $base-gray;
  border-radius: 16px;
  // padding: 5px 6px;

  p {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 12px !important;
    font-family: $thin-font-family !important;
  }

  // &:hover {
  //   background-color: $soft-gray;
  // }

  @media only screen and (max-width: 600px) {
    p {
      font-size: 13px;
      max-width: 90%;
    }
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.author-time {
  display: flex;
  align-items: center;
  color: $light-gray-blue;
  max-width: 80%;
  font-size: 12px !important;
  margin: 4px 0 0 0 !important;

  p {
    margin: 0 !important;
    padding: 0 !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }
}

.off-gray {
  color: #6b6b6b;
}

.relative {
  position: relative;
}
.absolute {
  position: absolute;
}
.regenerate-article {
  background: $white-blue;
  padding: 4px 24px 16px 0;
  // margin-top: 1rem;
}

button {
  font-family: $thin-font-family !important;
}

button:disabled {
  background-color: $off-white !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.tertiary-button {
  @include dark-blue-button();
  padding: 8px 12px !important;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  svg,
  img {
    // filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.tertiary-button-small {
  @include dark-blue-button();
  padding: 0 !important;
  border: none !important;
  color: $dark-black-blue;
  background-color: white;
  margin-right: 12px;
  svg,
  img {
    filter: invert(20%);
    transition: all 0.35s;

    &:hover {
      transform: scale(1.025);
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    }
  }

  &:hover {
    transform: scale(1);
    box-shadow: none;
  }

  &:disabled {
    border: none !important;
  }
}

.letter-spacing {
  //   letter-spacing: 0.25px;
}

.summary-button {
  @include gray-text-button();
  margin: 0 0.5rem;
  padding: 8px 16px;
  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}

.divider-dot {
  position: relative;
  bottom: 0.2rem;

  @media only screen and (max-width: 600px) {
    display: none;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.time {
  margin-left: 8px;

  @media only screen and (max-width: 600px) {
    display: none;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.news-container {
  padding: 0 40px;

  @media only screen and (max-width: 600px) {
    padding: 0 16px;
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
  }
}

.summary-section {
  position: absolute;
  left: -32px;
  top: 0;
  z-index: 1000;
  background-color: white;
}

.scroll-container {
  overflow-y: scroll;
}

.scroll-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.scroll-container::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.news-card {
  position: relative;
  min-height: 200px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 1rem 0;
  margin-bottom: 1rem;

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
  }
}

.news-card-medium {
  position: relative;
  min-height: 200px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 0 0 1rem 0;
  margin-bottom: 1rem;

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    height: 60px;
    overflow: none;
    text-overflow: ellipsis;
    margin-bottom: 8px;
  }
}

.card-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.card-row-med {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 8px;
  img {
    height: 12px;
    margin-right: 0.5rem;
    margin-top: 3px;
  }
}
.card:hover {
  // transform: scale(1.025);
}
.card-top-left {
  display: flex;
  font-size: 14px;
  font-family: $base-font-family;

  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}
.cover-photo {
  height: 96px;
  width: 100px;
  margin-left: 0.5rem;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: pointer;

  &:hover {
    opacity: 0.7;
  }

  @media only screen and (max-width: 600px) {
    margin-left: 0;
    margin-bottom: 4px;
  }
}

.cover-photo-ig {
  height: 250px;
  width: auto;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
}

.cover-photo-no-l-margin {
  height: 96px;
  width: 100px;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
}

.article-title {
  font-size: 17px;
  font-family: $base-font-family;
  font-weight: 200;
  line-height: 24px;
  letter-spacing: 0;
  color: $base-gray;
  margin: 12px 0;
  max-width: 450px;
  white-space: nowrap;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  cursor: pointer;

  &:hover {
    color: #6b6b6b;
  }

  @media only screen and (max-width: 600px) {
    font-size: 14px;
    max-width: 320px;
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
    max-width: 360px;
  }
}

.article-preview {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  height: 52px;
  line-height: 24px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;

  @media only screen and (max-width: 600px) {
    font-size: 13px;
    max-width: 320px;
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
    max-width: 360px;
  }
}

.tooltipped {
  position: relative;
  cursor: pointer;

  &::before {
    content: attr(tool-tip);
    position: absolute;
    bottom: 32px;
    left: 40px;
    transform: translateY(-50%);
    background-color: $dark-black-blue;
    color: white;
    padding: 5px;
    border-radius: 3px;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.4s;
  }

  &:hover::before {
    opacity: 1;
  }
}

.article-preview-medium {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  line-height: 24px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-top: 1rem;

  span {
    font-size: 12px;
    margin-right: 0.5rem;
  }

  @media only screen and (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;

    button {
      margin-top: 1.5rem;
      margin-left: 0 !important;
      width: 40vw;
    }
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.footer-icon-container {
  display: flex;
  align-items: center;
}

.small-photo {
  height: 18px;
  width: 18px;
  margin-bottom: 8px;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;

  margin-right: 4px;
}

.ellipsis-text-s {
  display: inline-block;
  max-width: 200px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;

  // @media only screen and (max-width: 600px) {
  //   max-width: 320px;
  // }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  // }
}

.ellipsis-text {
  max-width: 40vw;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;

  @media only screen and (max-width: 600px) {
    max-width: 320px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.a-text {
  text-decoration: none;
  color: #333333;
  font-family: $base-font-family;
  margin-top: 0 !important;

  &:hover {
    color: $lite-blue;
    text-decoration: underline;
  }
}

.ellipsis-text-bold {
  font-size: 22px;
  font-weight: 200;
  font-family: $base-font-family;
  max-height: 40px;
  max-width: 40vw;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-height: 32px;

  @media only screen and (max-width: 600px) {
    max-width: 80%;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.ellipsis-text-test {
  max-height: 40px;
  max-width: 45vw;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-height: 32px;
  font-size: 22px;
  font-weight: 200;
  font-family: $base-font-family;

  @media only screen and (max-width: 600px) {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    max-width: 320px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    max-width: 27vw;
  }
}

::v-deep .pre-text button {
  // border-bottom: 1px solid rgba(0, 0, 0, 0.128);
  background-color: white;
  padding: 5px 6px;
  border: 1px solid $dark-black-blue;
  color: $dark-black-blue;
  cursor: pointer;
  transition: all 0.5s;
  border-radius: 5px;

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: scale(1.02);
  }
}

::v-deep .pre-text {
  a {
    color: $grape;
    border-bottom: 1px solid $grape;
    font-family: $base-font-family;
    text-decoration: none;
    padding-bottom: 2px;

    &:hover {
      opacity: 0.7;
    }
  }

  strong,
  h1,
  h2,
  h3 {
    font-family: $base-font-family;
  }

  // ul {
  //   display: block;
  //   list-style-type: disc;
  //   margin-block-start: 0;
  //   margin-block-end: 0;
  //   margin-inline-start: 0px;
  //   margin-inline-end: 0px;
  //   padding-inline-start: 16px;
  //   unicode-bidi: isolate;
  // }

  // li {
  //   margin-top: -32px;
  //   padding: 0;
  // }
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;

  @media only screen and (max-width: 600px) {
    padding-bottom: 16px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.citation-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  min-height: 150px;

  @media only screen and (max-width: 600px) {
    padding-bottom: 16px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.filtered-blue {
  filter: invert(20%) sepia(28%) saturate(811%) hue-rotate(162deg) brightness(94%) contrast(81%);
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

.loading {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 1.5rem 0;

  p {
    margin-right: 8px;
  }
}

.loading-small {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
}

.loading-smallest {
  display: flex;
  align-items: center;
  padding: 0;
  border: none;
}

.loading-small-absolute {
  position: absolute;
  top: 70%;
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

  @media only screen and (max-width: 600px) {
    top: 100%;
  }
}

.right-arrow-footer {
  // padding: 2px 0;
  // height: 20px;
  height: 17px;
  margin-right: 12px;
  cursor: text;
}

h3 {
  font-size: 20px;
  margin: 0;
}

li {
  margin-top: 8px;
}

.bold {
  font-family: $base-font-family;
}

.gray-title {
  width: fit-content;
  border-radius: 8px;
  padding: 3px 8px;
  background-color: $off-white;
  margin-top: 0;
  margin-left: 8px;
  cursor: pointer;
}

.gray-title-no-margin {
  width: fit-content;
  border-radius: 4px;
  padding: 3px 8px;
  background-color: $soft-gray;
  margin-top: 0;
  cursor: pointer;
}

.no-margins {
  // padding-left: 16px;
  p {
    margin: 0;

    img {
      transform: rotate(180deg);
      transform: scaleX(-1);
      margin-right: 2px;
    }
  }
}
.small-container {
  // padding-left: 24px;
  // padding-right: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-size: 16px !important;
  line-height: 1.75;
  width: 100%;
  padding: 0 0 72px 0;

  @media only screen and (max-width: 600px) {
    padding: 32px 8px 12px 8px;
  }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  //   padding-left: 8px;
  //   padding-right: 8px;
  //   display: flex;
  //   align-items: center;
  //   justify-content: center;
  //   flex-direction: column;
  // }
}

.beta-span {
  span {
    background-color: $white-blue;
    color: black;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
  }
}

.blue-filter {
  filter: brightness(0) invert(23%) sepia(19%) saturate(984%) hue-rotate(162deg) brightness(92%)
    contrast(87%) !important;
}

// .img-blue {
//   background-color: $liter-blue !important;
//   color: $lite-blue;
//   img {
//     filter: invert(46%) sepia(77%) saturate(367%) hue-rotate(159deg) brightness(95%) contrast(97%) !important;
//   }
// }

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

.rotate {
  transform: rotate(180deg);
}

.rowed {
  display: flex;
  align-items: center;
  flex-direction: row;
  text-align: start !important;

  button:first-of-type {
    margin-right: 1rem;
  }
}

.row-top {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.row-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  background: $white-blue;
}

.row-end-bottom {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  width: 100%;
  margin-top: 1rem;
}

.rows {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  margin-top: 32px;
  gap: 7px;

  @media only screen and (max-width: 600px) {
  }

  @media only screen and (min-width: 601px) and (max-width: 1200px) {
  }

  @media only screen and (min-width: 1025px) {
  }
}

.row-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.content-body {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  overflow-y: scroll;
  scroll-behavior: smooth;
  z-index: 0;
  padding: 56px 32px 0 32px;
  font-size: 16px;
  width: 100%;
  height: 100%;

  @media only screen and (max-width: 600px) {
    padding: 32px 0;
  }
}

.content-body::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.content-body::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.contentShift {
  margin: 40px 15vw 40px 12vw !important;
  width: 54vw !important;
}

.contentShiftAlt {
  padding: 0 33vw 16px 10vw !important;
}

.sidebar-aside.open {
  transform: translateX(0);
}

.sidebar-aside {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 28vw;
  height: 100%;
  overflow-y: scroll;
  overflow-x: hidden;
  padding-top: 32px;
  background: white;
  right: 0;
  z-index: 100;
  transition: right 0.3s ease;
  transform: translateX(-100%);

  // position: absolute;
  // top: 0;
  // bottom: 0;
  // width: 28vw;
  // height: 100%;
  // overflow-y: scroll;
  // overflow-x: hidden;
  // padding-top: 32px;
  // background: white;
  // right: -100%;
  // z-index: 100;
  // transition: right 0.3s ease-in-out;

  // &.open {
  //   right: 0;
  // }

  @media (max-width: 768px) {
    width: 100%;
  }

  .section {
    padding: 0 8px;
    position: relative;
    overflow-y: scroll;
    margin-top: 12px;

    img {
      filter: invert(40%);
    }

    // div {
    //   margin-bottom: 16px;
    // }
  }

  .section-small {
    padding: 0 64px 0 16px;
    position: relative;
    margin-top: 12px;

    img {
      filter: invert(40%);
    }

    div {
      margin-bottom: 16px;
    }

    @media only screen and (min-width: 601px) and (max-width: 1024px) {
      padding: 0 0 0 24px;
    }
  }
}

.extra-padding-top {
  padding-top: 104px;
}

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 1s forwards;
}

.xxl-margin-top {
  margin-top: 32px;
  margin-bottom: 12px;

  @media only screen and (max-width: 600px) {
    margin-top: 16px;
    margin-bottom: 12px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.xxl-margin {
  margin-right: 4px;
  margin-top: 16px;

  @media only screen and (max-width: 600px) {
    margin-right: 0;
    margin-left: -8px;
    margin-top: 10px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.search {
  position: relative;
  font-family: $thin-font-family;
  font-size: 14px;
  height: 100%;
  padding: 32px 0 0 0;
  width: 100vw;

  .content-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    position: sticky;
    top: 0;
    background: $off-white;
    // border-bottom: 1px solid rgba(0, 0, 0, 0.128);
    padding: 24px 32px 8px 24px;
    z-index: 10;
  }

  .content-header-test {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    width: 100%;
    position: sticky;
    top: 0;
    background: $off-white;
    // border-bottom: 1px solid rgba(0, 0, 0, 0.128);
    padding: 56px 32px 8px 24px;
    z-index: 10;

    @media only screen and (max-width: 600px) {
      padding: 48px 0 0 0;
    }

    @media only screen and (min-width: 601px) and (max-width: 1024px) {
      padding: 48px 8px 8px 0;
    }
  }

  .main {
    width: 100vw;
    height: 95vh;
    position: relative;
    padding: 0 24px 24px 24px;
    overflow-y: hidden;
    transition: opacity 1s ease-out;
    opacity: 0;
    animation: fadeIn 1s forwards;

    .center-content {
      // display: flex;
      // align-items: center;
      // justify-content: center;
    }

    .body {
      width: 62vw;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      padding: 16px 16px 16px 40px;

      @media only screen and (max-width: 600px) {
        padding: 0;
        width: 100%;
      }

      @media only screen and (min-width: 601px) and (max-width: 1024px) {
      }
    }

    .widebody {
      width: 100%;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      padding: 0 20vw 16px 20vw;
      transition: padding 0.3s ease-in-out;

      @media only screen and (max-width: 600px) {
        padding: 0;
        width: 100%;
      }

      @media only screen and (min-width: 601px) and (max-width: 1024px) {
      }
    }

    .removed {
      display: none;
    }

    aside {
      position: absolute;
      right: 24px;
      top: 40px;
      bottom: 0;
      width: 35vw;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      padding-top: 32px;

      // @media only screen and (max-width: 600px) {
      //   display: none;
      // }

      @media only screen and (min-width: 601px) and (max-width: 1024px) {
        width: 40vw;
        right: 0;
        padding-left: 24px;
        top: 40px;
      }

      .section {
        // height: 30%;
        max-height: 50%;
        padding: 0 64px 0 16px;
        position: relative;
        overflow-y: scroll;
        margin-top: 12px;

        img {
          filter: invert(40%);
        }

        div {
          margin-bottom: 16px;
        }

        @media only screen and (min-width: 601px) and (max-width: 1024px) {
          padding: 0 0 0 24px;
        }
      }

      .section-small {
        // height: 30%;

        padding: 0 64px 0 16px;
        position: relative;
        margin-top: 12px;

        img {
          filter: invert(40%);
        }

        div {
          margin-bottom: 16px;
        }

        @media only screen and (min-width: 601px) and (max-width: 1024px) {
          padding: 0 0 0 24px;
        }
      }
    }

    .content {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      width: 100%;
      // min-height: 20vh;
      padding: 32px 32px 16px 64px;

      @media only screen and (max-width: 600px) {
        padding: 0;
      }

      @media only screen and (min-width: 601px) and (max-width: 1024px) {
        padding: 0;
      }
    }

    .gradient-border-top {
      border-top: 1px solid transparent;
      border-image: linear-gradient(
        to right,
        transparent 2%,
        rgba(0, 0, 0, 0.1) 2%,
        rgba(0, 0, 0, 0.1) 98%,
        transparent 98%
      );
      border-image-slice: 1;
    }

    .gradient-border-btm {
      border-bottom: 1px solid transparent;
      border-image: linear-gradient(
        to right,
        transparent 2%,
        rgba(0, 0, 0, 0.1) 2%,
        rgba(0, 0, 0, 0.1) 98%,
        transparent 98%
      );
      border-image-slice: 1;
    }

    .content-container {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      width: 100%;
      min-height: 20vh;
      padding: 8px 32px 96px 32px;
      overflow-y: scroll;
      overflow: visible;
      // margin-bottom: 16px;
      // border-bottom: 0.5px solid transparent;
      // border-image: linear-gradient(
      //   to right,
      //   transparent 2%,
      //   rgba(0, 0, 0, 0.1) 2%,
      //   rgba(0, 0, 0, 0.1) 98%,
      //   transparent 98%
      // );
      // border-image-slice: 1;

      @media only screen and (max-width: 600px) {
        padding: 0;
      }

      @media only screen and (min-width: 601px) and (max-width: 1024px) {
        padding: 0;
      }
    }

    .content-padding {
      position: relative;
      width: 100%;

      @media only screen and (max-width: 600px) {
        padding-bottom: 80px;
      }

      // &:hover {
      //   .absolute-bottom-right {
      //     display: block;
      //   }
      // }
    }

    .between {
      width: 100%;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      // padding-right: 30px;

      p {
        margin: 0;
      }
    }
  }

  .input {
    position: sticky;
    z-index: 2;
    top: 1.5rem;
    width: 50% !important;
    border-radius: 20px;
    border: 1px solid rgba(0, 0, 0, 0.135);
    font-family: $thin-font-family;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 7px 14px 7px 10px;
  }

  .search-input {
    border: none;
    outline: none;
    margin-left: 0.5rem;
    width: 100%;

    &:disabled {
      background: transparent;
    }
  }

  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  // @media only screen and (max-width: 600px) {
  //   flex-direction: column-reverse;
  //   align-items: center;
  //   justify-content: center;
  // }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  //   flex-direction: column;
  //   align-items: center;
  //   justify-content: center;
  // }

  // @media only screen and (min-width: 1025px) {
  // }
}

.header-p {
  font-family: $base-font-family;
  font-weight: 200;
  font-size: 16px;
  margin: 0;

  span {
    font-family: $thin-font-family;
  }
}

.header-alt {
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

.align-top {
  align-items: flex-start !important;
  height: 80vh;
}

.absolute-bottom-right {
  position: absolute;
  bottom: 8px;
  right: 4px;
}

.higher {
  bottom: 96px !important;
}

.empty-search {
  font-family: $thin-font-family;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $off-white;
  height: 100vh;
  width: 100vw;
  padding: 0 14vw;
  overflow: clip;

  @media only screen and (max-width: 600px) {
    padding: 0;
  }

  @media only screen and (min-width: 601px) and (max-width: 1200px) {
    padding: 0 10vw;
  }

  // @media only screen and (min-width: 1025px) {

  // }
}

.fit-content {
  height: fit-content !important;
}

.container {
  width: 50vw;
  height: 100vh;
  position: relative;

  @media only screen and (max-width: 600px) {
    width: 100vw;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 100vw;
  }
}

p {
  font-size: 16px;
  @media only screen and (max-width: 600px) {
    font-size: 14px !important;
  }
}

.container:first-of-type {
  border-right: 1px solid rgba(0, 0, 0, 0.1);

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    border: none;
  }
}

.header {
  padding: 16px 32px;
  width: 100%;
  background-color: white;
  z-index: 2;
}

.bottom-border {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.vertical-padding {
  padding: 1rem 40px;
}

.horiz-padding {
  padding: 0 40px;
}

.top-border {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.footer {
  padding: 16px 32px 32px 32px;
  width: 100%;
  background-color: white;
  z-index: 2;
}

.sticky-top {
  position: absolute;
  top: 0;
}

.mobile-header {
  @media only screen and (max-width: 600px) {
    // padding-right: 56px !important;
    // width: 100%;
    padding: 0;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

.small-buttons {
  button {
    @include dark-blue-button();
    background-color: white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 4px 6px;
    color: $dark-black-blue;
    font-size: 14px;
    margin-right: 8px;
  }
}

.padding-top {
  padding-top: 80px;
}

.padding-top-s {
  padding-top: 63.5px;
}

.sticky-bottom {
  position: absolute;
  bottom: 0;
}

.left-margin {
  margin-left: 8px;
}
.left-margin-m {
  margin-left: 12px;
}
.left-margin-l {
  margin-left: 16px;
}

.right-margin-s {
  margin-right: 4px;
}

.right-margin {
  margin-right: 8px;
}
.right-margin-m {
  margin-right: 12px;
}
.right-margin-l {
  margin-right: 16px;
}
.bottom-margin-xl {
  margin-bottom: 32px;
}

.text-width {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  p {
    font-size: 18px;
  }
}

.regular-font {
  font-family: $base-font-family;
}

.bottom-border-light {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 1rem;
}

.extra-padding {
  padding: 12px !important;
}

.centered {
  display: flex;
  align-items: center;
  justify-content: center;

  @media only screen and (max-width: 600px) {
    h1 {
      font-size: 24px;
    }

    .row {
      flex-flow: wrap;
    }
  }
}

.centered-column {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.centered-col {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 16px;
  width: 100%;
  height: 80%;
}

.gray-bg {
  background-color: $off-white;
}

.white-bg {
  background-color: white;
}

.lightblue-bg {
  background-color: $white-blue;
}

.dark-blue-bg {
  background-color: $dark-black-blue !important;
  img {
    filter: invert(100%) !important;
  }
}

.turq-bg {
  background-color: $turq !important;
}

.pink-bg {
  background-color: $pinky !important;
}

.purp-bg {
  background-color: $graper !important;
}

.orange-bg {
  background-color: $new-orange !important;
}

.void {
  cursor: not-allowed !important;
}

.img-text {
  img {
    margin-right: 16px;
    filter: invert(40%);
  }
}

.not-allowed-text {
  cursor: not-allowed !important;
  filter: blur(1px);
}

.switcher {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  background-color: $off-white;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  padding: 5px 2px;
  width: 60%;
  @media only screen and (max-width: 600px) {
    width: 70%;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 4px;
  border-radius: 16px;
  width: 100%;
  margin: 0 2px;
  cursor: pointer;
  color: $mid-gray;
  white-space: nowrap;
  font-weight: 400;
  font-size: 14px;

  @media only screen and (max-width: 600px) {
    font-size: 13px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.activesquareTile {
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background-color: $soft-gray;
  // color: $turq;
  font-family: $base-font-family;
}

.activesquare {
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background-color: $soft-gray;
  color: $dark-black-blue;
  font-family: $base-font-family;
}
.activeswitch {
  // background-color: white;
  // padding: 6px 4px;
  // box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background-color: $soft-gray;
  color: $dark-black-blue;
  font-family: $base-font-family;
  img {
    filter: none;
  }
}

.padding-right-x {
  padding-right: 24px !important;
}

.abs-right-img {
  background-color: $gray-blue !important;
  position: absolute;
  right: 0;
  padding: 4px !important;

  img {
    margin: 0 !important;
    filter: invert(100%) !important;
  }
}

.image-container {
  border-radius: 50%;
  padding: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: $off-white;
  img {
    filter: invert(40%);
  }

  &:hover {
    background-color: $soft-gray;
  }
}

.mobile-img {
  margin-top: 16px;
}

.image-container-nf {
  border-radius: 50%;
  padding: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: $off-white;

  &:hover {
    background-color: $soft-gray;
  }
}

.image-container-blue {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: $dark-black-blue;
  transition: all 0.2s;

  img {
    filter: brightness(0) invert(100%);
  }
}

input,
textarea {
  font-size: 16px !important;
}

.hide-mobile {
  @media only screen and (max-width: 600px) {
    display: none;
  }
}

.large-input-container-alt {
  // border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.025);
  border-radius: 20px;
  background-color: white;
  width: 100%;
  margin-bottom: 8px;

  @media only screen and (max-width: 600px) {
    width: 94vw !important;
  }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  //   width: 70vw !important;
  // }
}

.large-input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.025);
  border-radius: 28px;
  background-color: white;
  width: 100%;
  margin-bottom: 8px;

  @media only screen and (max-width: 600px) {
    width: 94vw !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 70vw !important;
  }
}

.input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 0;
  border-radius: 24px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;

  img {
    filter: invert(40%);
  }
}

.input-container-small {
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 2px 0;
  border-radius: 6px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  background-color: $off-white;

  img {
    filter: invert(40%);
  }

  input {
    background: transparent;
    padding-left: 16px !important;
  }
}

// .abs-placeholder {
//   width: 100%;
//   position: absolute;
//   left: 40px;
//   top: 8px;
//   pointer-events: none;
// }

.input-container-gray {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 14px 0 12px 0;
  border-radius: 20px;

  color: $base-gray;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  flex-direction: column;
  background-color: white;

  section {
    width: 100%;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    flex-direction: column;
  }

  img {
    filter: invert(40%);
  }

  @media only screen and (max-width: 600px) {
    margin-left: -4px;
    width: 100% !important;
  }
}

.area-input {
  width: 100%;
  margin-bottom: 0.25rem;
  max-height: 120px !important;
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
  width: 4px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.area-input::-webkit-scrollbar-track {
  margin-top: 24px;
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

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.mobile-col {
  @media only screen and (max-width: 925px) {
    display: flex;
    flex-direction: column-reverse;
    justify-content: flex-start;
    align-items: flex-start;
    width: 100%;
  }
}

.mobile-margin-left {
  @media only screen and (max-width: 925px) {
    margin-left: 16px;
  }
}

.space-evenly {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  width: 100%;
}

.borderless {
  border: none !important;

  &:disabled {
    border: none !important;
    cursor: text;

    img {
      opacity: 0.6;
    }
  }
}

.expanded-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 4px 0;
}

.expanded-item-column {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-direction: column;
  padding: 4px 0;
}

.example {
  width: 17vw;
  height: 18vh;
  padding: 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background-color: white !important;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  overflow: hidden;
  font-family: $thin-font-family;
  margin-bottom: 12px;

  p {
    margin: 0;
    font-size: 14px;
  }

  @media only screen and (min-width: 601px) and (max-width: 920px) {
    padding: 12px 8px;
  }

  &__header {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;

    p {
      font-family: $base-font-family;
      font-size: 16px;
    }
    img {
      margin-right: 8px;
    }

    @media only screen and (min-width: 601px) and (max-width: 1200px) {
      img {
        height: 10px;
        margin-right: 2px;
      }
      p {
        margin: 0;
        font-size: 14px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    @media only screen and (max-width: 600px) {
      img {
        height: 10px;
        margin-right: 2px;
      }

      p {
        margin: 0;
        font-size: 13px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }

  &__tag {
    padding: 0 6px;
    border-radius: 4px;
    background-color: $lite-blue;
    color: white;
    font-size: 11px;
    margin: 0;

    @media only screen and (min-width: 601px) and (max-width: 1200px) {
      padding: 0 4px;
      font-size: 9px !important;
    }

    @media only screen and (max-width: 600px) {
      font-size: 10px;
      padding: 0 4px;
    }
  }

  @media only screen and (max-width: 600px) {
    padding: 10px;
    height: 16vh;
    width: 48%;
    p {
      font-size: 12px !important;
    }
  }

  @media only screen and (min-width: 601px) and (max-width: 1200px) {
    width: 19vw;
    p {
      margin: 0;
      font-size: 12px !important;
    }
  }

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: scale(1.02);
  }
}

.example-small {
  min-width: 47%;
  padding: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  background-color: white;
  margin: 8px 0;
  cursor: pointer;
  transition: all 0.5s;
  img {
    margin-right: 12px;
  }
}
.example-small-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 96%;
  padding: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background-color: white;
  margin: 8px 0 !important;
  cursor: pointer;
  transition: all 0.5s;
  // img {
  //   margin-right: 12px;
  // }

  p {
    font-size: 14px !important;
  }

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transform: scale(1.015);
  }
}

.example-title {
  font-size: 14px;
  max-width: 240px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 6px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  background-color: white;
  margin: 0 !important;
  cursor: pointer;
  transition: all 0.5s;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // position: sticky;
  // top: 0;
  // z-index: 10;

  img {
    margin-right: 6px;
  }

  .example-row {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 0 !important;

    p {
      span {
        text-decoration: underline !important;
      }
    }
  }

  p {
    margin: 0;
    font-family: $base-font-family;
    font-weight: 200;
  }

  &:hover {
    background-color: $silver;
  }
}

.nobottomborder {
  border-bottom: none;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.example-body {
  max-height: 32%;
  overflow: scroll;
  background: white;
  width: 85%;
  padding: 4px 16px 12px 16px;
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  border-top: none;
  transition: opacity 0.5s ease-out;
  opacity: 0;
  animation: fadeIn 0.5s forwards;
  margin: 0 !important;
}

.example-text {
  font-size: 14px !important;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  padding-left: 12px;
  p {
    margin: 0;
  }
}

.example-full {
  font-size: 14px;
  width: 85%;
  padding: 11px 12px;
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background-color: white;
  margin: 0 0 8px 0;
  cursor: pointer;
  transition: all 0.5s;
  display: flex;
  align-items: center;
  justify-content: space-between;

  // @media only screen and (max-width: 600px) {
  //   width: 100%;
  // }

  // @media only screen and (min-width: 601px) and (max-width: 1250px) {
  //   width: 60vw !important;
  // }

  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: scale(1.02);
  }
}

.max-height {
  max-height: 30vh;
  overflow-y: scroll;
}

.custom-file-upload {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 4px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  color: black;
}

.file-img {
  margin-left: 12px;
  background-color: white;
  img {
    top: 12px;
    z-index: 5;
    margin-right: 8px;
  }
}

/* Hide the original file input */
.custom-file-upload input[type='file'] {
  padding: 0;
  margin: 0;
  display: none;
}
// p {
//   font-size: 14px;
// }

.horizontal-padding {
  padding: 0 34px 0 36px;

  @media only screen and (max-width: 600px) {
    padding: 0 16px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.horizontal-padding-s {
  padding: 0 16px;
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
.pointer {
  cursor: pointer !important;
}

.regen-modal {
  margin-top: 84px;
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

::v-deep .modal {
  @media only screen and (max-width: 600px) {
    // width: 90%;
  }
}
.message-text {
  font-family: $thin-font-family !important;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.blue-text-bg {
  background: $white-blue;
  padding: 16px 12px 0 12px;
  // border-radius: 4px;
  font-size: 16px;
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
.sticky-header {
  position: sticky;
  top: 0;
}

.paid-item:hover {
  cursor: pointer;
  opacity: 0.4;
}

.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.aligned-left {
  align-items: flex-start;
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

  // input {
  //   font-family: ;
  // }
}
.regen-body-title {
  font-size: 14px;
  margin: 0 0 0 0;
}
.padding {
  padding: 1rem 0;
}
.regen-body-text {
  resize: none;
  outline: none;
  border: 1px solid $soft-gray;
  border-radius: 8px;
  height: 4rem;
  width: 500px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 1rem;
  font-family: $thin-font-family !important;
}
.regen-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: -16px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
  font-family: $base-font-family;
  font-weight: 200;
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

.aligned-right {
  justify-content: flex-end;
}

.s-padding {
  padding: 0 0.25rem !important;
}
.area-input-outline {
  width: 300px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
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
  margin-right: 1rem;
  resize: none;
}

.full-width {
  width: 100%;
}

.wider {
  width: 100%;
}

.area-input-small {
  width: 80%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
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
}

.area-input-smallest {
  background-color: $off-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px !important;
  font-family: $thin-font-family !important;
  font-weight: 400;
  // border: none !important;
  border: 1px solid rgba(0, 0, 0, 0.1);
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  cursor: pointer;
}

// .area-input-smallest:last-of-type {
//   padding-left: 0.5rem;

//   @media only screen and (max-width: 600px) {
//     padding: 0;
//   }
// }

.close-x {
  cursor: pointer;
}

.close-x:hover {
  opacity: 0.4;
}
.inverted {
  filter: invert(100%);
}
.invert {
  filter: invert(40%) !important;
}
.top-right {
  position: absolute;
  top: 8px;
  right: 8px;
}

.carousel {
  position: relative;
  overflow: hidden;
  width: 300px;
  margin-top: 8px;
}

.carousel-slide {
  display: flex;
  transition: transform 0.5s ease;
}

.carousel-item {
  flex: 0 0 auto;
  width: 100%;
  text-align: start;
}

.car-dots {
  margin-top: 8px;
  position: sticky;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  // background-color: rgba(247, 245, 245, 0.644);
  padding: 3px 0;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.car-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ccc;
  margin: 0 5px;
  cursor: pointer;
}

.car-dot.active {
  background-color: $dark-black-blue;
}

.bio-modal {
  margin-top: 72px;
  @media only screen and (max-width: 600px) {
    margin-top: 62px;
  }

  width: 70vw;
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
  @media only screen and (max-width: 600px) {
    width: 95%;
    padding: 0;
  }

  header {
    // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
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
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    position: sticky;
    bottom: -1px;
    background-color: white;
    margin: 0;
    padding: 24px 0 0 0;

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
  line-height: 1.75;

  h2 {
    padding: 20px 0;
    margin-bottom: 0 !important;
    margin-block-start: 0 !important;
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
    margin-top: 0;
    padding: 0;
  }
}

.green-bg {
  background-color: white;
  border: 1px solid $dark-black-blue;
  // img {
  //   filter: invert(100%);
  // }
  //   img:hover {
  //     filter: invert(100%);
  //   }
}

.clicked {
  &:disabled {
    cursor: text !important;
    img {
      filter: invert(50%);
      cursor: text !important;
    }
  }
}

.cards-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-top: 16px;
  // flex-wrap: wrap;
  // padding: 24px 0;

  @media only screen and (max-width: 600px) {
    // gap: 8px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    // gap: 24px;
    width: 100%;
  }

  @media only screen and (min-width: 1025px) {
    // width: 15.6275vw;
    width: 100%;
  }
}

.silverbg {
  background-color: $silver !important;
}

.widecard {
  width: 51.25vw !important;

  @media only screen and (max-width: 600px) {
    width: 88vw !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}
.cardwidth {
  // width: 28.75vw !important;
  margin-top: -16px;
}

.card {
  width: 100%;
  padding: 0;
  border: none;
  border-radius: 5px;
  // transition: opacity 1s ease-out;
  // opacity: 0;
  // animation: fadeIn 1s forwards;
  overflow: hidden;
  margin: 0 !important;

  // @media only screen and (max-width: 600px) {
  //   width: 88vw;
  // }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  //   width: 47.5%;
  // }

  // @media only screen and (min-width: 1025px) {
  //   width: 48.5%;
  // }

  .main-body {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 16px 10px 0 10px;
    // min-height: 75px;
    // overflow: hidden;
    margin: 0 !important;

    img {
      filter: none;
    }
    p {
      margin: 6px 0;
      font-size: 14px !important;
      max-width: 20vw;
      max-height: 40px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2; /* Limits text to 2 lines */
      font-family: $base-font-family;
      font-weight: 200;

      @media only screen and (max-width: 600px) {
        max-width: 70vw;
      }
    }

    small {
      font-family: $base-font-family;
      font-size: 12px;
      color: $dark-black-blue;
      max-width: 20vw;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .main-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    // overflow: hidden;
    padding: 0 10px 8px 4px;
    width: 100%;
    margin: 0 !important;
  }

  &:hover {
    // box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    background-color: $silver;
  }
}

.card-photo-header-small {
  height: 150px;
  width: 100%;
  margin: 0;
  object-fit: cover;
  cursor: pointer;
  border-radius: 3px;
  z-index: 1;

  &:hover {
    opacity: 0.7;
  }
}

.card-photo-header {
  height: 50px;
  width: 60px;
  margin: 0;
  object-fit: cover;
  cursor: pointer;
  border-radius: 4px;

  z-index: 1;

  &:hover {
    opacity: 0.7;
  }
}

.mobile-body {
  @media only screen and (max-width: 600px) {
    display: flex;
    flex-direction: column-reverse !important;
    overflow-x: hidden !important;

    aside {
      display: flex;
      flex-direction: row !important;
      padding: 0;
      margin: 0 !important;
    }
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.skeleton-loader {
  padding: 56px 32px 32px 48px;
  overflow: hidden;

  @media only screen and (max-width: 600px) {
    padding: 72px 8px 32px 8px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    padding: 72px 0 32px 0;
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
  width: 250px;
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
  height: 200px;
  width: 100%;
}

.skeleton-img {
  height: 150px;
  width: 22%;
}

.photo-header-small {
  height: 40vh;
  width: 100%;
  margin: 0;
  object-fit: cover;
  // vertical-align: middle;
  // object-position: top;
  border-radius: 5px;
}

@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.absolute-arrows {
  position: fixed;
  bottom: 50px;
  left: 32%;
  z-index: 1000;
  display: flex;
  flex-direction: row;
  align-items: center;

  .arrow {
    cursor: pointer;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.7);
    padding: 4px;
    border-radius: 50%;
    user-select: none;
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      filter: invert(100%);
    }
  }
}

.img-container-button {
  cursor: pointer;
  padding: 6px 6px 2px 6px;
  border-radius: 50%;
  background-color: white;
  &:hover {
    background-color: $soft-gray;
  }

  img {
    margin: 0;
    padding: 0;
  }

  &:disabled {
    border: none !important;
  }
}

.img-container-stay {
  padding: 2px 7px 0 9px;
  border-radius: 50%;
  background-color: $soft-gray;

  img {
    margin: 0;
    padding: 0;
  }
}

.img-container-stay-alt {
  padding: 3px 5px 3px 7px;
  border-radius: 50%;
  background-color: $soft-gray;

  img {
    margin: 0;
    padding: 0;
  }
}

.img-container {
  cursor: pointer;
  padding: 1px 7px 0 7px;
  border-radius: 50%;
  &:hover {
    background-color: $soft-gray;
  }

  img {
    margin: 0;
    padding: 0;
  }
}

.lb-filter {
  filter: invert(45%) sepia(52%) saturate(1248%) hue-rotate(196deg) brightness(97%) contrast(90%) !important;
}

.lb-text {
  color: $lite-blue !important;
}

.lite-bg {
  background-color: $lite-blue;
  img {
    filter: invert(100%);
  }
}

.lbborder {
  // border: 1px solid $lite-blue;
}

.soft-gray-bg {
  background-color: $soft-gray !important;
}

.blk-text {
  color: $dark-black-blue;
}

.softer-gray-bg {
  background-color: $off-white !important;
}

.softgraybg {
  background-color: $dark-black-blue;
  color: white !important;
  img {
    filter: invert(100%);
  }
  // border: 0.5px solid rgba(0, 0, 0, 0.1);
}

.rotate-img {
  transform: rotate(180deg);
}

.container-left-above {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  left: 0;
  bottom: 40px;
  height: fit-content;
  width: 350px;
  padding: 16px;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;

  header {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    width: 100%;
    padding: 0 0 8px 0;
    p {
      margin: 0;
      font-family: $base-font-family;
    }
  }

  @media only screen and (max-width: 600px) {
    left: -32px;
  }
}

.container-right-abs {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  right: 0;
  top: 40px;
  height: 120px;
  width: 350px;
  padding: 32px 16px;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;

  p {
    margin: 0 0 8px 0;
  }
}

.image-bg {
  mix-blend-mode: multiply !important;
  background-color: white !important;
}

.container-right-above {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  right: 48px;
  bottom: 32px;
  height: 250px;
  width: 570px;
  padding: 0 0 16px 0;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 9;
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
    margin-top: 48px;
  }

  p {
    margin: 0;
    padding: 8px 16px;
    width: 100%;
    font-size: 13px;
    &:hover {
      background-color: $soft-gray;
      cursor: pointer;
    }
  }

  h3 {
    position: sticky;
    top: 0;
    background-color: white;
    font-family: $base-font-family;
    font-weight: 100;
    padding: 16px;
    width: 100%;
    z-index: 3;
  }
}

.container-left-above-alt {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  left: 0;
  bottom: 40px;
  height: 180px;
  width: 145%;
  padding: 0 0 16px 0;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 9;
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
    margin-top: 48px;
  }

  p {
    margin: 0;
    padding: 8px 16px;
    width: 100%;
    font-size: 13px;
    &:hover {
      background-color: $soft-gray;
      cursor: pointer;
    }
  }

  h3 {
    position: sticky;
    top: 0;
    background-color: white;
    font-family: $base-font-family;
    font-weight: 100;
    padding: 16px;
    width: 100%;
    z-index: 3;
  }
}

.container-left-below {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  left: 0;
  top: 40px;
  height: 220px;
  width: 400px;
  padding: 0 0 16px 0;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 9;
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
    margin-top: 48px;
  }

  p {
    margin: 0;
    padding: 8px 16px;
    width: 100%;
    font-size: 13px;
    &:hover {
      background-color: $soft-gray;
      cursor: pointer;
    }
  }

  h3 {
    position: sticky;
    top: 0;
    background-color: white;
    font-family: $base-font-family;
    font-weight: 100;
    padding: 16px;
    width: 100%;
    z-index: 3;
  }
}

.abs-bottom-right {
  position: absolute;
  bottom: 24px;
  right: 24px;

  img {
    filter: invert(22%) sepia(18%) saturate(1212%) hue-rotate(162deg) brightness(89%) contrast(82%);
  }
}

.sticky-bottom-right {
  position: sticky;
  bottom: 32px;
  right: 148px;
  z-index: 12;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  width: 80%;
}

.menu-wrapper {
  position: relative;
  &:hover {
    .help-menu {
      opacity: 1;
    }
  }
}

.help-menu {
  cursor: pointer;
  position: absolute;
  bottom: 32px;
  right: 0;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.275);
  border-radius: 4px;
  width: 160px;

  h4 {
    margin: 0;
    margin: 12px;
  }
  div {
    width: 100%;
    padding: 8px 12px;
    display: flex;
    flex-direction: row;
    align-items: center;

    img {
      filter: invert(40%);
      margin-right: 8px;
    }

    &:hover {
      background-color: $off-white;

      a {
        text-decoration: underline;
      }
    }
  }

  div:last-of-type {
    padding-bottom: 16px;
  }

  a {
    text-decoration: none;
    font-size: 13px;
    color: $dark-black-blue;
  }
}

.share-link {
  text-decoration: none;
  font-size: 13px;
  color: $dark-black-blue;

  &:hover {
    color: $lite-blue;
    text-decoration: underline;
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

.scrolltainer {
  &::-webkit-scrollbar {
    width: 2px;
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
}

.blueish-filter {
  filter: invert(26%) sepia(74%) saturate(1811%) hue-rotate(193deg) brightness(97%) contrast(95%) !important;
}

.turq-filter {
  filter: invert(56%) sepia(96%) saturate(331%) hue-rotate(139deg) brightness(90%) contrast(87%);
}

.turq-text {
  font-size: 14px;

  span {
    color: #3b8ec0;
    font-family: $base-font-family;
  }

  &:hover {
    span {
      text-decoration: underline;
    }

    cursor: pointer;
  }
}

.pink-filter {
  filter: invert(43%) sepia(88%) saturate(559%) hue-rotate(280deg) brightness(86%) contrast(83%) !important;
}

.pink-text {
  color: $pinky !important;
}

.blue-text {
  color: $lite-blue;
}

.purple-filter {
  filter: invert(51%) sepia(13%) saturate(1063%) hue-rotate(217deg) brightness(96%) contrast(84%);
}

.purple-bg {
  background-color: $grapest;
  border-radius: 50%;
  padding: 7px 6px 0 6px;
}

filter ::selection {
  background-color: $lite-blue !important;
  color: white;
}
::v-deep ::selection {
  background-color: $lite-blue !important;
  color: white;
}

.absolute-icon {
  position: absolute;
  right: 2px;
  top: 2px;
  background-color: $dark-black-blue;
  border-radius: 100%;
  padding: 3px 0 3px 3px;
  cursor: pointer;
  visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    // filter: invert(46%) sepia(35%) saturate(2345%) hue-rotate(323deg) brightness(106%) contrast(96%);
    filter: invert(100%);
    margin: 0;
    padding: 0;
  }
}

.dropdown-select {
  position: relative;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 8px;
  width: 100%;
  z-index: 900000000000000000000000;

  &-header {
    font-size: 14px;
    width: 100% !important;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    padding: 4px 0;
  }

  &-body-up {
    position: absolute;
    top: 8px;
    left: 0;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
    height: 230px;
    background-color: white;
    width: 100%;
    z-index: 900000000000000000000001;
    overflow-y: scroll;

    &::-webkit-scrollbar {
      width: 5px !important;
      height: 0px;
    }
    &::-webkit-scrollbar-thumb {
      background-color: $soft-gray;
      box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
      border-radius: 6px;
    }

    &::-webkit-scrollbar-track {
      margin-top: 48px;
    }
  }

  &-body {
    position: absolute;
    top: 44px;
    left: 0;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
    height: 250px;
    background-color: white;
    z-index: 100000000;
    overflow-y: scroll;

    &::-webkit-scrollbar {
      width: 5px !important;
      height: 0px;
    }
    &::-webkit-scrollbar-thumb {
      background-color: $soft-gray;
      box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
      border-radius: 6px;
    }

    &::-webkit-scrollbar-track {
      margin-top: 48px;
    }
  }

  &-item {
    padding: 8px 12px;

    &:hover {
      color: $light-gray-blue;
      cursor: pointer;
    }
  }

  &-bottom {
    position: sticky;
    bottom: 0;
    padding: 8px 12px;
    width: 100%;
    background-color: white;
  }

  &-top {
    position: sticky;
    top: 0;
    padding: 8px;
    width: 100%;
    background-color: white;
  }
}

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  cursor: pointer;
  background: url('~@/assets/images/downArrow.svg') no-repeat calc(100% - 8px) center;
  background-size: 16px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

/* Hide default HTML checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: 0.4s;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: '';
  height: 12px;
  width: 12px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: 0.4s;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: $turq;
}

input:focus + .slider {
  box-shadow: 0 0 1px $turq;
}

input:checked + .slider:before {
  -webkit-transform: translateX(16px);
  -ms-transform: translateX(16px);
  transform: translateX(16px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

input[type='time'] {
  position: relative;
  z-index: 1;
}

input[type='time'].has-placeholder::before {
  content: attr(data-placeholder);
  color: #999;
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  z-index: 0;
}

input[type='time'].has-placeholder::-webkit-datetime-edit {
  color: transparent;
}

.journalistSection {
  p {
    margin: 6px 0;
    padding: 0;
    span {
      font-family: $base-font-family;
    }
  }
}

.journalistCol {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 24px;
}

.big-chat-bubble {
  width: fit-content;
  border-radius: 12px;
  padding: 8px 16px;
  margin: 12px 0;
  background-color: white;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);
}

select {
  width: 200px;
  padding: 8px 12px;
  font-family: $thin-font-family;
  font-size: 14px;
  color: $dark-blue;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
  appearance: none;
  background-image: url('~@/assets/images/dropdown.svg');
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;

  &:hover {
    background-color: $soft-gray;
  }

  &:focus {
    outline: none;
    border-color: $dark-black-blue;
  }
}

.file-input-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-family: $thin-font-family;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.file-input {
  display: none;
}

// .secondary-button {
//   @include dark-blue-button();
//   padding: 8px 12px;
//   border: 1px solid rgba(0, 0, 0, 0.2);
//   border-radius: 16px;
//   color: $dark-black-blue;
//   background-color: white;
//   margin-right: -2px;
// }

.mobile-padding {
  @media only screen and (max-width: 600px) {
    padding: 0 8px !important;
  }
}

.file-name {
  margin-top: 10px;
  font-size: 14px;
  color: #333333;
  font-weight: 400;
}

.chat-window {
  height: 96vh;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: space-evenly;
  padding: 32px 10vw 0 10vw;

  &__header {
    width: 100%;
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 24px 0 12px 0;
    p {
      font-family: $base-font-family;
      font-size: 18px !important;
    }
  }

  &__body {
    height: 100%;
    width: 100%;
    overflow-y: scroll;
    padding: 0 4px;
  }

  &__footer {
    position: sticky;
    bottom: 0;
    width: 100%;
    padding: 24px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  &__chat-bubble {
    line-height: 1.5;
    width: fit-content;
    border-radius: 20px;
    padding: 8px 16px;
    margin: 12px 0;
    background-color: white;
    box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);

    img {
      margin-right: 6px;
    }

    p {
      margin: 0;
    }
  }
}
.med-modal {
  width: 55vw !important;
}
.med-container {
  width: 48vw !important;
  padding: 0 16px 0 16px !important;
}

.bold-text {
  font-family: $base-font-family !important;
}
.thin-text {
  font-family: $thin-font-family !important;
  margin: 0 !important;
}

.thin-span {
  span {
    font-family: $thin-font-family !important;
  }
}

.circle-img {
  border-radius: 50%;
  height: 14px;
  width: 14px;
}

.abs-container {
  position: absolute;
  top: 36px;
  right: 8px;
}
.lessTop {
  top: 0 !important;
}
.lesserTop {
  top: -24px !important;
}
.abs-input-text {
  position: absolute;
  left: 20px;
  background-color: white;
  cursor: pointer;
  color: $lite-blue;
  font-family: $base-font-family;

  p {
    padding-bottom: 4px;
  }

  &:hover {
    text-decoration: underline;
  }
}

.alt-btn {
  padding: 5px 10px;

  &:hover {
    background-color: $dark-black-blue;
    color: white;

    img {
      filter: invert(100%);
    }
  }

  &:disabled {
    color: $dark-black-blue !important;
    img {
      filter: none !important;
    }
    opacity: 0.9 !important;
  }
}

.space-between-top {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
}

.containered {
  z-index: 100000;
  position: absolute;
  top: 96px;
  right: 25vw;
  width: 50vw;
  background-color: white;
  padding: 16px 12px 16px 16px;
  border-radius: 5px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 9px 11px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
  font-family: $thin-font-family;
  height: 80vh;
  overflow-y: scroll;
  p {
    margin: 8px 0;
  }

  small {
    color: $base-gray;
  }

  &__top {
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
    padding-bottom: 12px;
  }

  &::-webkit-scrollbar {
    width: 4px; /* Width of the scrollbar */
  }

  &::-webkit-scrollbar-thumb {
    background-color: transparent; /* Default: invisible */
    box-shadow: none; /* No shadow when not scrolling */
    border-radius: 6px;
    height: 24px; /* Ensures the thumb is always 24px in height */
    transition: background-color 0.2s ease, box-shadow 0.2s ease; /* Smooth visibility change */
  }

  &:hover::-webkit-scrollbar-thumb,
  &:active::-webkit-scrollbar-thumb {
    background-color: #d3d3d3; /* Clean light gray when scrolling */
    box-shadow: inset 2px 2px 4px 0 rgba(0, 0, 0, 0.1); /* Subtle shadow for visibility */
  }

  &::-webkit-scrollbar-track {
    margin-top: 12px; /* Top margin for the track */
  }

  @media only screen and (max-width: 600px) {
    right: 12px;
    width: 94vw !important;
  }
}

.bold-font {
  font-family: $base-font-family !important;
}

.abs-top-right {
  position: absolute;
  top: -12px;
  right: -12px;
  cursor: pointer;
  background-color: $dark-black-blue;

  img {
    filter: invert(100%);
  }
}
.img-mar {
  img {
    margin-right: 4px;
  }
}

.mobile-min {
  @media only screen and (max-width: 600px) {
    min-width: 70vw !important;
  }
}

.top-mar-mobile {
  margin-top: 16px;

  @media only screen and (max-width: 600px) {
    margin-top: 8px;
  }
}

.no-mar-mobile {
  @media only screen and (max-width: 600px) {
    margin-left: 4px !important;
  }
}

.mobile-top {
  @media only screen and (max-width: 600px) {
    top: 24px !important;
  }
}

.mobile-top-s {
  @media only screen and (max-width: 600px) {
    top: 22px !important;
  }
}

.pinkbg {
  background-color: $pinky !important;
  margin: 0;
}

.widetip {
  width: 200px !important;
}

.pulse-dot {
  margin-right: 14px;
}

.omni-load {
  display: flex;
  flex-direction: column;
}

.pulse {
  color: $lite-blue;
  img {
    filter: invert(45%) sepia(52%) saturate(1248%) hue-rotate(196deg) brightness(97%) contrast(90%) !important;
    box-shadow: 0 0 0 0 $lite-blue;
    transform: scale(1);
    animation: pulsate 1.25s infinite;
    border-radius: 100%;
  }
}

@keyframes pulsate {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 $dark-green;
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
  }
}
// .pulser {
//   box-shadow: 0 0 0 0 $dark-green;
//   transform: scale(1);
//   animation: pulsate 1.25s infinite;
// }
</style>