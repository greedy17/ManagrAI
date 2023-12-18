<template>
  <div ref="pitchTop" class="pitches">
    <!-- paidModal -->
    <Modal v-if="paidModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="closePaidModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Upgrade to Pro</h3>
              <h5 class="regen-body-title">
                You have reached your usage limit for the month. Please upgrade your plan.
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="instructions" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div class="cancel-button" @click="closePaidModal">Close</div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>
    <!-- resetModal -->
    <Modal v-if="resetModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="closeResetModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Are you sure?</h3>
              <h5 class="regen-body-title">This writing style will be permanently removed.</h5>
            </div>
            <!-- <textarea v-autoresize v-model="instructions" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div class="cancel-button" @click="closeResetModal">Cancel</div>
            <div class="reset-button mar-left gray-border" @click="resetWritingStyle">Delete</div>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="inputModalOpen" class="paid-modal">
      <div style="width: 600px; min-height: 275px" class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title">Learn Writing Style</h4>
            <p class="regen-header-subtitle">
              Provide a sample of the writing style you want to emulate
            </p>
          </div>
          <div v-if="!savingStyle" class="pointer" @click="toggleLearnInputModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div class="paid-body">
          <input
            class="input-text"
            placeholder="Name your writing style..."
            type="text"
            v-model="styleName"
            :disabled="savingStyle"
          />
          <div class="sample-row">
            <div style="width: 600px" class="input-container">
              <div class="input-row relative">
                <textarea
                  :disabled="savingStyle"
                  maxlength="8000"
                  class="area-input text-area-input"
                  style="padding: 16px 0 0 0"
                  placeholder="Paste sample here..."
                  v-model="sample"
                  v-autoresize
                />

                <div class="absolute-count">
                  <small>{{ remainingCharsSample }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <div class="input-row">
            <button :disabled="savingStyle" @click="toggleLearnInputModal" class="secondary-button">
              Cancel
            </button>
            <button :disabled="savingStyle" @click="saveWritingStyle" class="primary-button">
              <img
                v-if="savingStyle"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
              />
              {{ savingStyle ? 'Learning' : 'Learn' }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="journalistModalOpen" class="paid-modal" style="z-index: 1000000s">
      <div style="width: 500px; min-height: 275px" class="regen-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">
              {{ !journalists ? 'Find Journalists' : 'Journalists' }}
            </h3>
            <p class="regen-header-subtitle">
              {{ !journalists ? 'Provide additional details below' : 'Journalist details' }}
            </p>
          </div>
          <div v-if="!loadingJournalists" class="pointer" @click="toggleJournalistModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div
          :class="loadingJournalists ? 'opaque' : ''"
          v-if="!journalists"
          class="paid-body input-width"
        >
          <label for="pub">Publication Type</label>
          <input
            class="input-text"
            placeholder="(e.g, tier 1, tier 2, industry specific, niche, etc.)"
            type="text"
            v-model="pubType"
            :disabled="loadingJournalists"
            id="pub"
          />

          <label for="beat">Beat</label>
          <input
            class="input-text"
            placeholder="(e.g, technology, health, lifestyle, etc.)"
            type="text"
            v-model="beat"
            :disabled="loadingJournalists"
            id="beat"
          />

          <label for="loc">Location</label>
          <input
            class="input-text"
            placeholder="(e.g, National, Atlanta, D.C, etc.)"
            type="text"
            v-model="location"
            :disabled="loadingJournalists"
            id="loc"
          />
        </div>

        <div v-else class="paid-body">
          <pre v-html="journalists" class="pre-text" style="font-size: 14px"></pre>
        </div>

        <div class="paid-footer align-right">
          <div class="input-row">
            <button
              :disabled="loadingJournalists"
              @click="toggleJournalistModal"
              class="secondary-button"
            >
              {{ !journalists ? 'Cancel' : 'Close' }}
            </button>
            <button
              v-if="!journalists"
              @mouseenter="changeJournalText"
              @mouseleave="defaultJournalText"
              :disabled="loadingJournalists || !isPaid"
              @click="getJournalists"
              class="primary-button no-transitions"
            >
              <img
                v-if="loadingJournalists"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
              />
              {{ journalText }}
            </button>

            <button v-else @click="copyJournalText" class="primary-button no-transitions">
              {{ copyTip }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <div :class="loading ? 'opaque' : ''" class="center">
      <div class="relative">
        <Transition name="slide-fade">
          <div v-if="showBanner" style="left: -64px; top: 0; width: 120px" class="templates">
            <p>Saved Successfully!</p>
          </div>
        </Transition>
      </div>

      <div class="centered dark-blue-bg" style="width: 100%; color: white">
        <div style="width: 50%; padding: 0 32px">
          <h2 style="margin: 0">Create content</h2>
          <p>Generate content that mirrors your writing style.</p>

          <div class="input-container" v-clickOutsideInstructionsMenu>
            <div class="input-row relative">
              <div class="main-text">Instructions</div>

              <textarea
                :disabled="loading"
                maxlength="2000"
                style="margin: 0"
                class="area-input text-area-input"
                :placeholder="instructionsPlaceholder"
                v-model="output"
                v-autoresize
                @focus="showInstructionsDropdown($event)"
              />

              <div @click="toggleStyleDropdown" class="drop-text pointer">
                <p class="ellipsis-text" style="margin: 0">
                  {{ writingStyleTitle ? writingStyleTitle : 'Select Style' }}
                </p>
                <img
                  v-if="!showStyleDropdown"
                  src="@/assets/images/downArrow.svg"
                  class="inverted"
                  height="14px"
                  alt=""
                />
                <img
                  class="rotate-img inverted"
                  v-else
                  src="@/assets/images/downArrow.svg"
                  height="14px"
                  alt=""
                />
              </div>

              <div v-if="showStyleDropdown" class="content-dropdown">
                <div class="drop-container">
                  <section v-if="userWritingStyles.length">
                    <p
                      style="
                        margin-bottom: 0;
                        padding-bottom: 8px;
                        cursor: text;
                        color: #2f4656;
                        font-size: 15px;
                      "
                    >
                      Select writing style
                    </p>
                    <div
                      @mouseenter="setIndex(i)"
                      @mouseLeave="removeIndex"
                      @click="addWritingStyle(style.style, style.title)"
                      class="dropdown-item"
                      v-for="(style, i) in userWritingStyles"
                      :key="i"
                      style="padding: 4px 0"
                    >
                      <p style="padding: 0 16px; margin: 0">
                        {{ style.title }}
                      </p>

                      <div @click="openResetModal(style.id)" class="absolute-icon">
                        <img
                          v-if="hoverIndex === i"
                          src="@/assets/images/trash.svg"
                          height="12px"
                          alt=""
                        />
                      </div>
                    </div>

                    <div style="padding: 8px 0">
                      <button
                        @mouseenter="changeStyleText"
                        @mouseleave="defaultStyleText"
                        style="margin-bottom: 8px; width: 86%"
                        @click="toggleLearnInputModal"
                        class="primary-button"
                      >
                        {{ styleText }}
                      </button>
                    </div>
                  </section>
                  <section style="padding: 8px 0" v-else>
                    <p class="dropdown-item">Saved writing styles will appear here</p>
                    <button
                      @mouseenter="changeStyleText"
                      @mouseleave="defaultStyleText"
                      style="margin-bottom: 8px"
                      @click="toggleLearnInputModal"
                      class="primary-button"
                    >
                      {{ styleText }}
                    </button>
                  </section>
                </div>
              </div>

              <div class="absolute-count">
                <small>{{ remainingChars }}</small>
              </div>

              <button
                :disabled="loading || !this.output"
                @click="generatePitch"
                style="
                  margin: 0;
                  margin-left: 8px;
                  margin-top: 2px;
                  border: none !important;
                  background-color: transparent;
                  cursor: pointer;
                "
              >
                <img
                  v-if="loading || !this.output"
                  style="margin: 0"
                  src="@/assets/images/paper-plane-top.svg"
                  height="14px"
                  alt=""
                  class="grow faded"
                />

                <img
                  v-else
                  style="margin: 0"
                  src="@/assets/images/paper-plane-full.svg"
                  height="14px"
                  alt=""
                  class="grow"
                />
              </button>
            </div>
            <div v-if="showingInstructionsDropdown" class="dropdown">
              <small style="padding: 8px 0" class="gray-text">Word count:</small>
              <div style="padding: 0 0 4px 0; margin-bottom: 8px">
                <input
                  :disabled="loading"
                  class="number-input"
                  placeholder="Optional..."
                  v-model="characters"
                  type="number"
                  max="1500"
                  @input="enforceMax"
                />
              </div>
              <small style="padding-top: 8px" class="gray-text">Example Instructions</small>
              <div
                @click="addInstructionsSuggestion(suggestion)"
                class="dropdown-item"
                v-for="(suggestion, i) in filteredInstructionsSuggestions"
                :key="i"
              >
                <p>
                  {{ suggestion }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- <div class="input-container" v-clickOutsideCharacterMenu>
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/a.svg" height="12px" alt="" />
            Words
          </div>

          <input
            :disabled="loading"
            class="area-input"
            placeholder="Provide word count..."
            v-model="characters"
            type="number"
            max="1500"
            @focus="showCharacterDropdown($event)"
          />
        </div>
        <div v-if="showingCharacterDropdown" class="dropdown">
          <small style="padding-top: 8px" class="gray-text">Character Suggestions</small>
          <div
            @click="addCharacterSuggestion(suggestion)"
            class="dropdown-item"
            v-for="(suggestion, i) in filteredCharacterSuggestions"
            :key="i"
          >
            <p>
              {{ suggestion }}
            </p>
          </div>
        </div>
      </div>

      <div class="input-container" v-clickOutsideTypeMenu>
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/blog-text.svg" height="14px" alt="" />
            Style
          </div>

          <input
            :disabled="loading"
            style="overflow-x: hidden"
            class="area-input"
            placeholder="Select a writing style..."
            v-model="writingStyleTitle"
            @focus="showTypeDropdown"
          />
        </div>
        <div v-if="showingTypeDropdown" class="dropdown">
          <small style="padding-top: 8px" class="gray-text"
            >{{
              userWritingStyles.length
                ? `Saved writing styles: ${userWritingStyles.length}`
                : 'Saved writing styles will appear here:'
            }}
          </small>
          <section v-if="userWritingStyles.length">
            <div
              @mouseenter="setIndex(i)"
              @mouseLeave="removeIndex"
              @click="addWritingStyle(style.style, style.title)"
              class="dropdown-item"
              v-for="(style, i) in userWritingStyles"
              :key="i"
            >
              <p>
                {{ style.title }}
              </p>

              <div @click="openResetModal(style.id)" class="absolute-icon">
                <img v-if="hoverIndex === i" src="@/assets/images/trash.svg" height="12px" alt="" />
              </div>
            </div>
            <div style="padding: 16px 0" class="centered">
              <button
                @mouseenter="changeStyleText"
                @mouseleave="defaultStyleText"
                style="margin-bottom: 8px; width: 160px"
                @click="toggleLearnInputModal"
                class="primary-button extra-padding"
              >
                <img class="invert" src="@/assets/images/sparkle.svg" height="12px" alt="" />
                {{ styleText }}
              </button>
            </div>
          </section>
          <section v-else>
            <div class="dropdown-footer">
              <button
                @mouseenter="changeStyleText"
                @mouseleave="defaultStyleText"
                style="margin-bottom: 8px; width: 160px"
                @click="toggleLearnInputModal"
                class="primary-button extra-padding"
              >
                <img class="invert" src="@/assets/images/sparkle.svg" height="12px" alt="" />
                {{ styleText }}
              </button>
            </div>
          </section>
        </div>
      </div>

      <footer>
        <button :disabled="loading" @click="clearData" class="secondary-button">Clear</button>
        <button :disabled="loading || !this.output" @click="generatePitch" class="primary-button">
          <img
            v-if="loading"
            class="rotate"
            height="14px"
            src="@/assets/images/loading.svg"
            alt=""
          />
          {{ loading ? 'Submitting' : 'Submit' }}
        </button>
      </footer> -->
    </div>

    <div style="padding-top: 0" class="center gray-bg">
      <div v-if="loading" style="width: 50%; margin-left: 4rem; margin-top: 1rem">
        <div style="width: 100%" class="row">
          <!-- <p class="summary-load-text">Generating {{ type }}...</p> -->
          <p class="summary-load-text">Generating content...</p>
        </div>

        <div class="summary-preview-skeleton shimmer">
          <!-- <div class="content">
            <div class="meta-wide"></div>
            <div class="meta-shorter"></div>
            <div class="meta-shortest"></div>
          </div> -->
          <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </div>
      <div v-else style="width: 50%; padding: 0 16px 0 32px">
        <div class="pitch-container">
          <Transition name="slide-fade">
            <div v-if="showUpdateBanner" class="templates">
              <p>Pitch saved successfully!</p>
            </div>
          </Transition>
          <div class="title-container">
            <!-- <div @click="resetSearch" class="back">
            <img src="@/assets/images/back.svg" height="18px" width="18px" alt="" />
          </div> -->

            <p class="sub-text text-truncation">
              {{ !pitch ? 'Your content will appear below.' : `${savedOutput}` }}
            </p>
            <p v-if="pitch" class="sub-text">{{ pitch.split(' ').length }} words</p>
          </div>

          <div class="title-bar">
            <div v-if="!showSaveName" class="row">
              <div v-if="pitch" class="gray-text">AI-generated content</div>
              <!-- <button
                :disabled="loading || !pitch"
                @click="toggleRegenerate"
                v-if="!regenerating"
                class="secondary-button"
              >
                <img
                  v-if="contentLoading"
                  class="rotate"
                  height="14px"
                  src="@/assets/images/loading.svg"
                  alt=""
                />
                {{ contentLoading ? 'Regenerating' : 'Regenerate' }}
              </button> -->
              <!-- <div style="width: 600px" class="row" v-else>
                <input
                  :disabled="loading"
                  placeholder="provide additional instructions..."
                  autofocus
                  class="regen-input"
                  type="textarea"
                  style="padding-top: 10px; padding-bottom: 10px"
                  v-model="instructions"
                />
                <button style="margin-left: 8px" @click="toggleRegenerate" class="secondary-button">
                  Cancel
                </button>
                <button
                  style="margin-left: -4px"
                  @click="regeneratePitch"
                  class="primary-button no-mar"
                >
                  Submit
                </button>
              </div> -->
              <!-- <div class="save-wrapper" v-if="!loading && !savingPitch && !pitchSaved">
                <button
                  @click="toggleSaveName"
                  v-if="!regenerating"
                  :disabled="loading || savingPitch || pitchSaved || !pitch"
                  class="primary-button no-mar"
                >
                  <img
                    v-if="savingPitch"
                    class="rotate"
                    height="12px"
                    src="@/assets/images/loading.svg"
                    alt=""
                  />
                  {{ savingPitch ? 'Saving' : 'Save' }}
                </button>
                <div style="margin-left: -50px" class="save-tooltip">
                  {{ pitch ? 'Save this version' : 'Create content first' }}
                </div>
              </div> -->
              <!-- <div v-else>
                <button
                  @click="toggleSaveName"
                  v-if="!regenerating"
                  :disabled="loading || savingPitch || pitchSaved || !pitch"
                  class="primary-button no-mar"
                >
                  <img
                    v-if="savingPitch"
                    class="rotate"
                    height="12px"
                    src="@/assets/images/loading.svg"
                    alt=""
                  />
                  {{ savingPitch ? 'Saving' : 'Save' }}
                </button>
              </div> -->
            </div>

            <div v-else class="row">
              <input
                autofocus
                class="area-input-outline"
                placeholder="Name your pitch"
                v-model="pitchName"
              />

              <button
                @click="showSaveName = false"
                :disabled="loading || savingPitch || pitchSaved"
                class="secondary-button"
                style="margin-right: 0"
              >
                Cancel
              </button>

              <button
                @click="createSavedPitch"
                :disabled="loading || savingPitch || pitchSaved"
                class="primary-button"
                style="margin-left: 1rem"
              >
                Save
              </button>
            </div>

            <!-- <div
              @click="copyText"
              v-if="pitch && true /*!regenerating*/"
              class="wrapper circle-border"
            >
              <img
                style="cursor: pointer"
                class="right-mar img-highlight"
                src="@/assets/images/clipboard.svg"
                height="12px"
                alt=""
              />
              <div style="margin-left: -14px" class="tooltip">{{ copyTip }}</div>
            </div> -->
            <div style="display: flex">
              <div style="margin-right: 0.5rem">
                <div
                  @click="toggleJournalistModal"
                  class="wrapper circle-border white-bg"
                  :class="{ 'bluee-bg': journalists }"
                  v-if="pitch"
                >
                  <img
                    style="cursor: pointer"
                    class="right-mar img-highlight"
                    src="@/assets/images/profile.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -22px" class="tooltip">
                    {{ !journalists ? 'Find Journalists' : 'View Journalists' }}
                  </div>
                </div>
                <div v-else class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="right-mar img-highlight"
                    src="@/assets/images/profile.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Create content first</div>
                </div>
              </div>

              <div style="margin-right: 0.5rem">
                <div
                  @click="toggleSaveName"
                  class="wrapper circle-border white-bg"
                  v-if="pitch && !savingPitch && !pitchSaved"
                >
                  <img
                    height="14px"
                    src="@/assets/images/disk.svg"
                    alt=""
                    class="filter-green img-highlight"
                  />
                  <div class="tooltip" style="margin-left: -14px">
                    {{ 'Save' }}
                  </div>
                </div>
                <div v-else-if="!pitch" class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="right-mar img-highlight"
                    src="@/assets/images/disk.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Create content first</div>
                </div>
              </div>

              <div>
                <div @click="copyText" class="wrapper circle-border white-bg" v-if="pitch">
                  <img
                    style="cursor: pointer"
                    class="right-mar img-highlight"
                    src="@/assets/images/clipboard.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -22px" class="tooltip">{{ copyTip }}</div>
                </div>
                <div v-else class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="right-mar img-highlight"
                    src="@/assets/images/clipboard.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Create content first</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="pitch" class="centered" style="width: 100%; padding: 0px 32px 16px 56px">
        <div v-if="pitch && !loading" style="width: 50%">
          <pre
            style="margin-top: -4px; padding-top: 16px; border-top: 1px solid rgba(0, 0, 0, 0.1)"
            v-html="pitch"
            class="pre-text"
          ></pre>
        </div>
        <div
          style="margin: 1rem 0 0 0; padding-top: 0; padding-bottom: 0; border-radius: 28px"
          id="instructions"
          class="input-container-chat"
          v-if="pitch && !loading"
        >
          <div style="padding-top: 0" class="input-row">
            <div class="main-text-img">
              <img style="margin-top: 4px" src="@/assets/images/comment.svg" height="18px" alt="" />
            </div>

            <textarea
              style="margin: 0; padding-top: 1px"
              class="area-input text-area-input"
              id="instructions-text-area"
              placeholder="What would you like to edit?"
              v-model="instructions"
              :rows="1"
              v-autoresize
            />

            <div @click="instructions = ''" class="cancel-container">
              <img src="@/assets/images/add.svg" class="lip-img invert-dark-blue" />
            </div>
            <button
              @click="regeneratePitch"
              :disabled="!instructions"
              style="
                margin: 0;
                margin-left: 8px;
                border: none !important;
                background-color: transparent;
              "
            >
              <img
                v-if="!instructions"
                style="margin: 0"
                src="@/assets/images/paper-plane-top.svg"
                height="17px"
                alt=""
                class="faded"
              />

              <img
                v-else
                style="margin: 0"
                src="@/assets/images/paper-plane-full.svg"
                height="13px"
                alt=""
                class="grow filtered-blue"
              />
            </button>
          </div>

          <!-- <div v-if="showingPromptDropdown" class="dropdown">
            <div style="padding-top: 4px; padding-bottom: 4px">
              <small class="gray-text">Popular Prompts</small>
            </div>

            <div
              class="dropdown-item"
              v-for="(suggestion, i) in filteredPromptSuggestions"
              :key="i"
              @click="addPromptSuggestion(suggestion)"
            >
              <p>
                {{ suggestion }}
              </p>
            </div>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
import User from '@/services/users/'

export default {
  name: 'Pitches',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      loadingJournalists: false,
      journalists: null,
      location: null,
      beat: null,
      pubType: null,
      journalText: 'Search',
      journalistModalOpen: false,
      contentLoading: false,
      showStyleDropdown: false,
      styleName: null,
      hoverIndex: null,
      styleText: 'Learn writing style',
      deleteId: null,
      inputModalOpen: false,
      showBanner: false,
      writingStyleTitle: null,
      type: '',
      output: '',
      savedOutput: '',
      persona: '',
      briefing: '',
      characters: null,
      pitch: null,
      loading: false,
      regenerating: false,
      paidModal: false,
      showingTypeDropdown: false,
      showingAudienceDropdown: false,
      showingCharacterDropdown: false,
      showingInstructionsDropdown: false,
      storedEvent: null,
      storedPlaceholder: '',
      optionalPlaceholder: 'Optional',
      instructionsPlaceholder: 'What would you like written?',
      typeSuggestions: [
        `Press Release`,
        `Media Pitch`,
        `Blog Post`,
        `LinkedIn Post`,
        `Twitter Post`,
        `Email`,
      ],
      audienceSuggestions: [
        `Millenial moms`,
        `Vegans`,
        `College students`,
        `Local writers in Georgia`,
        `Gen Z`,
        `Health and wellness enthusiast`,
      ],
      characterSuggestions: [`250`, `500`, `750`, `1000`, `1500`],
      instructionsSuggestions: [
        `Create a media pitch for XXX about ...`,
        `Issue a press release on behalf of XXX about ...`,
        // `Use the text below to generate XXX for XXX ...`,
        `Re-write the content below using my writing style:`,
        `List 10 journalists along with pitching tips, that would be interested in writing about the content below:`,
      ],
      instructions: '',
      copyTip: 'Copy',
      textToCopy: '',
      showSaveName: false,
      savingPitch: false,
      pitchName: '',
      savedPitch: null,
      showUpdateBanner: false,
      showInput: false,
      sample: '',
      savingStyle: false,
      writingStyle: null,
      resetModal: false,
    }
  },
  watch: {
    currentPitch(newVal, oldVal) {
      if (newVal.id !== (oldVal ? oldVal.id : null)) {
        this.setPitch(newVal)
      }
    },
  },
  beforeDestroy() {
    this.$store.commit('setGeneratedContent', null)
  },
  methods: {
    async getJournalists() {
      this.loadingJournalists = true
      try {
        await Comms.api
          .getJournalists({
            type: this.pubType,
            beat: this.beat,
            location: this.location,
            content: this.pitch,
          })
          .then((response) => {
            console.log(response)
            this.journalists = response.journalists
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingJournalists = false
      }
    },
    toggleJournalistModal() {
      this.journalistModalOpen = !this.journalistModalOpen
    },
    enforceMax() {
      if (this.characters > 1500) {
        this.characters = 1500
      }
    },
    toggleStyleDropdown() {
      this.showStyleDropdown = !this.showStyleDropdown
    },
    test() {
      console.log(this.userWritingStyles)
    },
    setIndex(i) {
      this.hoverIndex = i
    },
    removeIndex() {
      this.hoverIndex = null
    },
    async saveWritingStyle() {
      this.savingStyle = true
      try {
        await Comms.api
          .saveWritingStyle({
            example: this.sample,
            title: this.styleName,
          })
          .then((response) => {
            console.log('response.style', response.style)
            this.showBanner = true
            setTimeout(() => {
              this.showBanner = false
            }, 2000)
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.sample = ''
        this.styleName = ''
        this.toggleLearnInput()
        this.savingStyle = false
        this.refreshUser()
        this.toggleLearnInputModal()
      }
    },
    async resetWritingStyle() {
      this.savingStyle = true
      this.sample = ''
      this.writingStyleTitle = ''
      this.closeResetModal()
      try {
        await Comms.api.deleteWritingStyle({ style_id: this.deleteId })
        this.toggleLearnInput()
      } catch (e) {
        console.log(e)
      } finally {
        this.savingStyle = false
        this.deleteId = null
        this.writingStyle = null
        this.refreshUser()
      }
    },

    changeJournalText() {
      if (!this.isPaid) {
        this.journalText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultJournalText() {
      if (!this.isPaid) {
        this.journalText = 'Search'
      } else {
        return
      }
    },

    changeStyleText() {
      if (!this.isPaid) {
        this.styleText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultStyleText() {
      if (!this.isPaid) {
        this.styleText = 'Learn writing style'
      } else {
        return
      }
    },
    openResetModal(id) {
      this.resetModal = true
      this.deleteId = id

      if (this.showStyleDropdown === true) {
        this.showStyleDropdown = false
      }
    },
    closeResetModal() {
      this.resetModal = false
    },
    toggleLearnInput() {
      if (this.isPaid) {
        this.showInput = !this.showInput
      }
    },
    toggleLearnInputModal() {
      if (this.isPaid) {
        this.inputModalOpen = !this.inputModalOpen

        if (this.showStyleDropdown === true) {
          this.showStyleDropdown = false
        }
      }
    },
    async copyText() {
      try {
        await navigator.clipboard.writeText(this.pitch)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyJournalText() {
      try {
        await navigator.clipboard.writeText(this.journalists)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },

    toggleSaveName() {
      this.showSaveName = !this.showSaveName
    },
    resetSearch() {
      this.pitch = null
      this.writingStyle = ''
      this.writingStyleTitle = ''
      this.output = ''
      this.persona = ''
      this.briefing = ''
      this.instructions = ''
    },
    showTypeDropdown() {
      this.showingTypeDropdown = true
    },
    hideTypeDropdown() {
      this.showingTypeDropdown = false
    },
    showAudienceDropdown() {
      this.showingAudienceDropdown = true
    },
    hideAudienceDropdown() {
      this.showingAudienceDropdown = false
    },
    showCharacterDropdown(e) {
      // this.storedEvent = e
      // this.storedPlaceholder = e.target.placeholder
      // e.target.placeholder = ''
      this.optionalPlaceholder = ''
      this.showingCharacterDropdown = true
    },
    hideCharacterDropdown() {
      this.optionalPlaceholder = 'Optional'
      // this.storedEvent.target.placeholder = this.storedPlaceholder
      // this.storedPlaceholder = ''
      this.showingCharacterDropdown = false
    },
    showInstructionsDropdown(e) {
      // this.storedEvent = e
      // this.storedPlaceholder = e.target.placeholder
      // e.target.placeholder = ''
      this.instructionsPlaceholder = ''
      this.showingInstructionsDropdown = true
    },
    hideInstructionsDropdown() {
      // this.storedEvent.target.placeholder = this.storedPlaceholder
      // this.storedPlaceholder = ''
      this.instructionsPlaceholder = 'What would you like written?'
      this.showingInstructionsDropdown = false
    },
    addWritingStyle(ex, title) {
      this.writingStyle = ex
      this.writingStyleTitle = title
      this.showStyleDropdown = false
      this.hideTypeDropdown()
    },
    addAudienceSuggestion(ex) {
      this.persona = ex
      this.hideAudienceDropdown()
    },
    addCharacterSuggestion(ex) {
      this.characters = ex
      this.hideCharacterDropdown()
    },
    addInstructionsSuggestion(ex) {
      this.output = ex
      this.hideInstructionsDropdown()
    },
    scrollToTop() {
      setTimeout(() => {
        this.$refs.pitchTop.scrollIntoView({ behavior: 'smooth' })
      }, 450)
    },
    openPaidModal() {
      this.paidModal = true
    },
    closePaidModal() {
      this.paidModal = false
    },
    goToContact() {
      window.open('https://managr.ai/contact', '_blank')
    },
    toggleRegenerate() {
      this.regenerating = !this.regenerating
    },
    async createSavedPitch() {
      this.showSaveName = false
      this.savingPitch = true
      try {
        const response = await Comms.api.savePitch({
          name: this.pitchName || this.pitch.slice(0, 60),
          user: this.user.id,
          type: this.type,
          audience: this.persona,
          generated_pitch: this.pitch,
          instructions: this.output,
        })
        if (response.id) {
          // this.searchId = response.id
          this.showUpdateBanner = true
          this.savedPitch = {
            name: response.name,
            user: this.user.id,
            type: this.type,
            audience: this.persona,
            generated_pitch: this.pitch,

            instructions: this.output,
          }
          await this.$store.dispatch('getPitches')
        }
      } catch (e) {
        console.log(e)
      } finally {
        // this.showUpdateBanner = true
        this.savingPitch = false
        setTimeout(() => {
          this.showUpdateBanner = false
        }, 2000)
      }
    },
    async regeneratePitch() {
      this.regenerating = false
      this.contentLoading = true
      this.loading = true
      const tempPitch = this.pitch
      this.pitch = ''
      this.savedOutput = this.instructions
      try {
        await Comms.api
          .regeneratePitch({
            pitch: tempPitch,
            instructions: this.instructions,
          })
          .then((response) => {
            this.pitch = response.pitch
          })
      } catch (e) {
        console.log('ERROR CREATING PITCH::', e)
      } finally {
        // this.clearData()
        this.instructions = ''
        this.contentLoading = false
        this.loading = false
        this.scrollToTop()
      }
    },
    async generatePitch() {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal()
        return
      }
      this.journalists - null
      this.loading = true
      this.showStyleDropdown = false
      try {
        await Comms.api
          .generatePitch({
            type: this.type,
            instructions: this.output,
            audience: this.persona,
            style: this.writingStyle,
            chars: this.characters,
          })
          .then((response) => {
            this.savedOutput = this.output
            this.pitch = response.pitch
            this.scrollToTop()
            this.$store.commit('setGeneratedContent', null)
          })
          .then((response) => {
            this.refreshUser()
          })
          .then((response) => {
            this.$store.dispatch('getPitches')
          })
      } catch (e) {
        console.log('ERROR CREATING PITCH', e)
      } finally {
        // this.clearData()
        this.loading = false
        this.scrollToTop()
      }
    },
    setPitch(pitch) {
      this.pitch = pitch.generated_pitch
      this.type = pitch.type
      this.output = pitch.instructions
      this.persona = pitch.audience

      // this.generatePitch()
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
    clearData() {
      this.type = ''
      this.output = ''
      this.persona = ''
      this.briefing = ''
      this.sample = ''
      this.writingStyle = ''
    },
  },
  computed: {
    userWritingStyles() {
      return this.$store.state.user.writingStylesRef
    },
    remainingChars() {
      return 2000 - this.output.length
    },
    remainingCharsBrief() {
      return 2000 - this.briefing.length
    },
    remainingCharsSample() {
      return 8000 - this.sample.length
    },
    user() {
      return this.$store.state.user
    },
    filteredTypeSuggestions() {
      if (!this.type) return this.typeSuggestions
      return this.typeSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.type.toLowerCase()),
      )
    },
    filteredAudienceSuggestions() {
      if (!this.persona) return this.audienceSuggestions
      return this.audienceSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.persona.toLowerCase()),
      )
    },
    filteredCharacterSuggestions() {
      if (!this.characters) return this.characterSuggestions
      return this.characterSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.characters.toLowerCase()),
      )
    },
    filteredInstructionsSuggestions() {
      if (!this.output) return this.instructionsSuggestions
      return this.instructionsSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.output.toLowerCase()),
      )
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
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
    currentPitch() {
      return this.$store.state.currentPitch
    },
    pitchSaved() {
      if (this.savedPitch && this.pitch && this.savedPitch.generated_pitch === this.pitch) {
        return true
      } else if (
        this.pitch &&
        this.currentPitch &&
        this.currentPitch.generated_pitch === this.pitch
      ) {
        return true
      } else {
        return false
      }
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
    clickOutsideInstructionsMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideInstructionsDropdown()
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
    clickOutsideTypeMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideTypeDropdown()
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
    clickOutsideAudienceMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideAudienceDropdown()
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
    clickOutsideCharacterMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideCharacterDropdown()
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::placeholder {
  color: $mid-gray;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.title-container {
  position: relative;
  display: flex;
  justify-content: space-between;
  width: 100%;
  @media only screen and (max-width: 600px) {
    margin-top: 1rem;
  }
}

.relative {
  position: relative;
}

.absolute-count {
  position: absolute;
  bottom: 4px;
  right: 3px;
  font-size: 10px;
  color: $light-gray-blue;
  // background-color: $white-blue;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  // border-radius: 4px;
  // padding: 2px 4px;
}

.no-text-margin {
  margin: 0;
}

.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
}

// .sub-text {
//   color: $light-gray-blue;
//   margin: 8px 0 16px 0;
//   font-size: 14px;

//   font-family: $thin-font-family;
//   span {
//     font-weight: normal;
//     word-wrap: break-word;
//   }
// }

.sub-text {
  // color: $light-gray-blue;
  margin: 8px 0;
  font-size: 14px;
  font-family: $thin-font-family;

  span {
    font-weight: 200;
    word-wrap: break-word;
  }
  @media only screen and (max-width: 600px) {
    text-align: center;
  }
}

.title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 1.75rem;
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
  text-align: start !important;

  button:first-of-type {
    margin-right: 1rem;
  }
}

.pitch-container {
  padding: 16px 0 2px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  @media only screen and (max-width: 600px) {
    width: 80%;
  }
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;

  margin-right: 8px;
}

.pre-text {
  // background-color: $white-blue;
  border-radius: 4px;
  // padding: 16px;
  margin: 0;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.dark-blue-bg {
  background-color: $dark-black-blue;
  padding: 23px 0 30px;
}

.pitches {
  background-color: white;
  width: 100vw;
  height: 100vh;
  padding: 0;
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  font-family: $thin-font-family;
  color: $chat-font-color;
  @media only screen and (max-width: 600px) {
    height: 91vh;
    padding: 12px 36px 0 36px;
  }
}

.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  // height: 100%;
  padding-top: 32px;
  font-size: 14px;
  color: $dark-black-blue;
  gap: 24px;
  @media only screen and (max-width: 600px) {
    padding-top: 4px;
  }
}

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 1rem;
  margin-top: 0.95rem;
  border-radius: 6px;
  // width: 675px;
  width: 100%;
  min-height: 4.9rem;
  background-color: $offer-white;
  color: $base-gray;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}
.input-container-chat {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem;
  border-radius: 6px;
  width: 50%;
  background-color: $offer-white;
  color: $base-gray;
  position: relative;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}

.number-input {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: $offer-white;
  padding: 6px 2px;
  outline: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family;
  font-weight: 400;
  margin-top: 8px;
  border-radius: 4px;
  width: 80px;
}

.number-input::placeholder {
  font-size: 11px;
}
.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input:disabled {
  cursor: not-allowed;
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

.regen-input {
  resize: none;
  outline: none;
  border: 1px solid $soft-gray;
  border-radius: 6px;
  width: 400px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 8px 1rem;
  font-family: $base-font-family;
  @media only screen and (max-width: 600px) {
    // position: static;
    width: 23%;
  }
}
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
  align-items: center;
}
.main-text {
  width: 132px;
  display: flex;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding-right: 1rem;
  margin: 0;
  font-size: 13px;
  color: $dark-black-blue;
  svg,
  img {
    margin-right: 8px;
    filter: invert(40%);
  }
}

.drop-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  max-width: 100px;
  margin: 0;
  font-size: 12px;
  color: $dark-black-blue;
  background-color: $off-white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 4px;
  svg,
  img {
    margin-left: 4px;
    filter: invert(40%);
  }
}

.drop-text:hover {
  opacity: 0.7;
}

footer {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-bottom: 1rem;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  white-space: nowrap;
  margin-left: 1rem;

  img {
    margin-right: 0.5rem;
  }
}

.extra-padding {
  padding: 12px 8px;
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
}

.input-text {
  width: 600px;
  margin: 1rem 0;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family !important;
  background-color: $offer-white;
  font-size: 13px;
  padding: 10px 20px 10px 18px;
  outline: none;
}

.input-text ::placeholder {
  color: red !important;
}

.input-width {
  input {
    width: 500px !important;
  }
}

.reset-button {
  @include white-button-danger();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  margin-right: -2px;
}

.mar-left {
  margin-left: 1rem;
}

.blue-bg {
  padding: 16px 0;
  background-color: $white-blue;
}

.opaque {
  opacity: 0.75;
}

.img-highlight {
  filter: invert(40%);

  &:hover {
    filter: none;
  }
}

.wrapper {
  display: flex;
  align-items: center;
  // background-color: red;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -20px;
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

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
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

.save-wrapper {
  display: flex;
  align-items: center;
  // background-color: red;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.save-wrapper .save-tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: 15px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 130px;
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

/* This bridges the gap so you can mouse into the save-tooltip without it disappearing */
.save-wrapper .save-tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.save-wrapper .save-tooltip:after {
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

.save-wrapper:hover .save-tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .save-wrapper .save-tooltip {
  display: none;
}

.lte8 .save-wrapper:hover .save-tooltip {
  display: block;
}

.back {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0.75rem;
  left: -56px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 3px 2px;
  cursor: pointer;

  img {
    filter: invert(40%);
  }
  @media only screen and (max-width: 600px) {
    // position: static;
    width: 1.5rem;
    left: 50%;
    top: -2rem;
    // margin-bottom: 1rem;
  }
}

.summary-load-text {
  font-family: $thin-font-family;
  font-size: 14px;
}

.summary-preview-skeleton {
  width: 100%;
  // min-width: 400px;
  padding: 8px 0;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  @media only screen and (max-width: 600px) {
    width: 80%;
  }
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  display: inline-block;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
}

.meta-wide {
  width: 100%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shorter {
  width: 80%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shortest {
  width: 60%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.extra-margin-top {
  // margin-top: 16px;
  margin-top: 5.5rem;
  @media only screen and (max-width: 600px) {
    margin-top: 0rem;
  }
}
.paid-modal {
  margin-top: 132px;
}
.regen-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  color: $base-gray;
  font-family: $thin-font-family;

  label {
    font-size: 14px;
  }
}
.paid-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  position: sticky;
  top: 0;
  background-color: white;
}
.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.regen-header-title {
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 12px;
  color: $light-gray-blue;
  margin: 0.5rem 0;
}
.pointer {
  cursor: pointer;
}
.paid-body {
  margin: 0.5rem 0;
  scroll-behavior: smooth;
  overflow-y: scroll;
}
.regen-body-title {
  margin: 0 0 0 0;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
}
.align-right {
  justify-content: flex-end !important;
}
.paid-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  padding-bottom: 8px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}
.gray-border {
  border: 1px solid $soft-gray;
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
.dropdown {
  padding: 8px 0 16px 0;
  position: relative;
  height: fit-content;
  max-height: 232px;
  width: 100%;
  top: 8px;
  overflow-y: scroll;
  overflow-x: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  scroll-behavior: smooth;
}

.dropdown::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  display: none;
}
.dropdown::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.dropdown:hover::-webkit-scrollbar {
  display: block;
}

.paid-body::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.paid-body::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.paid-body:hover::-webkit-scrollbar {
  display: block;
}

.dropdown-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 8px;
  width: 100%;
  min-height: 100px;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 13px;
  z-index: 2300;

  p {
    margin: 0;
  }
}

.ellipsis-text {
  max-width: 100px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.dropdown-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  padding: 8px 0;
  width: 100%;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 13px;
  // z-index: 2300;

  p {
    margin: 0;
    padding: 0;
  }

  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }

  &:hover {
    opacity: 0.7;
  }
}

.absolute-icon {
  position: absolute;
  padding-left: 4px;
  background: transparent;
  background-color: white;
  // opacity: 0;
  right: 0;
  cursor: pointer;

  img {
    &:hover {
      filter: invert(66%) sepia(47%) saturate(6468%) hue-rotate(322deg) brightness(85%)
        contrast(96%);
    }
  }
}

.gray-text {
  color: $mid-gray;
}
.mar-top {
  margin-top: 1rem;
}
.text-area-input::placeholder {
  // padding-top: 1rem;
}
.text-area-input {
  padding-top: 1.25rem;
}
.divider {
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 675px;
  margin-top: 1rem;
  @media only screen and (max-width: 600px) {
    width: 100vw;
  }
}

.divider-text {
  position: absolute;
  top: -24px;
  left: 44%;
  z-index: 20;
  background-color: white;
  padding: 4px 16px;
  border-radius: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  @media only screen and (max-width: 600px) {
    left: 39%;
  }
}
.content {
  // width: 80%;
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
  font-family: $base-font-family;
  font-weight: 400;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  margin-right: 1rem;
  resize: none;
}
.no-mar {
  margin: 0;
}
.primary-button:disabled {
  background-color: $soft-gray;
}

.no-transitions:hover {
  scale: 1 !important;
}

button:disabled {
  background-color: $off-white !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
  cursor: not-allowed !important;
  opacity: 0.7;
}
.circle-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 100%;
  padding: 5px 6px;
  background-color: $white-blue;
  img {
    margin: 0 !important;
  }
}
.slide-fade-enter-active {
  transition: all 0.2s ease-in;
}

.slide-fade-leave-active {
  transition: all 0.1s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(100px);
}
.templates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: 8px;
  left: 45%;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 2000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.invert {
  filter: invert(96%);
}

.sample-row {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.img-margin {
  img {
    margin: 0 4px;
  }
}

.thin-font {
  font-family: $thin-font-family;
}

.green-filter {
  filter: invert(66%) sepia(20%) saturate(1059%) hue-rotate(101deg) brightness(89%) contrast(93%);
}

.faded {
  filter: invert(55%);
}

.gray-bg {
  padding: 16px 0;
  background-color: $off-white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.rotate-img {
  transform: rotate(180deg);
}

.content-dropdown {
  width: 260px;
  position: absolute;
  top: 48px;
  right: 32px;
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

.grow:hover {
  transform: scale(1.2);
  box-shadow: 2px 4px 32px rgba($color: $black, $alpha: 0.3);
  opacity: 0.7;
}
.grow {
  transition: all 0.2s;
}
.loading {
  display: flex;
  // justify-content: center;
  align-items: center;
  border-radius: 6px;
  // padding: 1.5rem 0.75rem;
  padding: 1.5rem 0;
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
.white-bg {
  background: white;
}
.bluee-bg {
  background: $white-blue !important;
}
.absolute-right {
  position: absolute;
  right: 8px;
  top: -48px;
}
.text-truncation {
  width: 60%;
  white-space: nowrap;
  overflow-x: hidden;
  text-overflow: ellipsis;
}
.main-text-img {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  filter: invert(40%);
  margin: 0;
  padding-right: 1rem;
}
.cancel-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $offer-white;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 6px;
  cursor: pointer;
  // box-shadow: 1px 1px 3px 1px rgba(0, 0, 0, 0.1);
  margin: 12px 0;

  img {
    transform: rotate(45deg);
  }
  transition: all 0.2s;
}
.lip-img {
  height: 14px;
  padding: 0;
  margin: 0;
  z-index: 5500;
}
.invert-dark-blue {
  filter: invert(22%) sepia(51%) saturate(390%) hue-rotate(161deg) brightness(92%) contrast(87%);
}
.filtered-blue {
  filter: invert(20%) sepia(28%) saturate(811%) hue-rotate(162deg) brightness(94%) contrast(81%);
}
</style>