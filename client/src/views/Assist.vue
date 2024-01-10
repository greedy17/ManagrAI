<template>
  <div ref="" class="main">
    <Modal v-if="modalOpen" class="process-modal">
      <div style="width: 510px" class="modal-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">Create a process</h3>
            <p class="regen-header-subtitle">Select from the options below</p>
          </div>
          <div @click="toggleModal" v-if="!loading" class="pointer">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div class="paid-body input-width">
          <label for="name">Name</label>
          <input
            v-model="processName"
            class="input-text"
            placeholder="Name your process..."
            type="text"
            id="name"
            :disabled="loading"
          />

          <label for="">Saved search</label>
          <div>
            <Multiselect
              style="width: 500px; height: 0.5rem; margin: 1rem 0"
              :options="searches"
              :show-labels="false"
              placeholder="Choose one"
              label="name"
              track-by="id"
              v-model="processSearchId"
              :disabled="loading"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
          </div>

          <label for="loc">Content type</label>
          <input
            class="input-text"
            placeholder="(e.g., media pitch, press release, blog post, issue statement, etc.)"
            type="text"
            id="loc"
            v-model="processType"
            :disabled="loading"
          />

          <label for="">Writing style</label>

          <div>
            <Multiselect
              style="width: 500px; height: 0.5rem; margin: 1rem 0"
              :options="writingStyles"
              :show-labels="false"
              placeholder="Choose one"
              label="title"
              track-by="style"
              v-model="processStyle"
              :disabled="loading"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
          </div>

          <label for="loc">Additional details</label>
          <input
            class="input-text"
            placeholder="(e.g., company name & description, personal preferences, etc.)"
            type="text"
            id="loc"
            v-model="processDetails"
            :disabled="loading"
          />
        </div>

        <div class="paid-footer">
          <div class="row">
            <button @click="toggleModal" class="secondary-button">Cancel</button>
            <button
              :disabled="
                loading ||
                !processDetails ||
                !processName ||
                !processStyle ||
                !processType ||
                !processSearchId
              "
              @click="createProcess"
              class="primary-button no-transitions"
            >
              <img
                v-if="loading"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
              />
              Save
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="journalistModalOpen" class="process-modal">
      <div style="min-height: 275px; width: 510px" class="modal-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">
              {{ !journalists ? 'Find Journalists/Influencers' : 'Journalists/Influencers' }}
            </h3>
            <p class="regen-header-subtitle">
              {{
                !journalists
                  ? 'Provide additional details below'
                  : 'Journalist/Influencer details and pitching tips'
              }}
            </p>
          </div>
          <div v-if="!loading" class="pointer" @click="toggleJournalistModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div :class="loading ? 'opaque' : ''" v-if="!journalists" class="paid-body input-width">
          <label for="pub">Publication Type</label>
          <input
            class="input-text"
            placeholder="(e.g., Tier 1, industry-specific, niche, TikTok influencers, etc.)"
            type="text"
            v-model="pubType"
            :disabled="loading"
            id="pub"
          />

          <label for="beat">Beat</label>
          <input
            class="input-text"
            placeholder="(e.g., Technology, health, lifestyle, etc.)"
            type="text"
            v-model="beat"
            :disabled="loading"
            id="beat"
          />

          <label for="loc">Location</label>
          <input
            class="input-text"
            placeholder="(e.g., National, Atlanta, D.C, etc.)"
            type="text"
            v-model="location"
            :disabled="loading"
            id="loc"
          />
        </div>

        <div v-else class="paid-body">
          <pre v-html="journalists" class="pre-text" style="font-size: 14px"></pre>
        </div>

        <div class="paid-footer">
          <div style="margin-right: 0.5rem" class="row">
            <button :disabled="loading" @click="toggleJournalistModal" class="secondary-button">
              {{ !journalists ? 'Cancel' : 'Close' }}
            </button>
            <button
              v-if="!journalists"
              @mouseenter="changeJournalText"
              @mouseleave="defaultJournalText"
              :disabled="loading || !isPaid"
              @click="getJournalists"
              class="primary-button no-transitions"
            >
              <!-- <img
                v-if="loading"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
              /> -->
              {{ journalText }}
              <div style="margin-left: 4px" v-if="loading" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>

            <button v-else @click="copyJournalText" class="primary-button no-transitions">
              {{ copyTip }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="feedbackModalOpen" class="process-modal">
      <div style="min-height: 275px" class="modal-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">
              {{
                !feedback
                  ? 'Optimize Content'
                  : regeneratedFeedback && feedback
                  ? 'Optimized Content'
                  : 'Optimize Content'
              }}
            </h3>
            <p class="regen-header-subtitle">
              {{
                !feedback
                  ? 'Get content feedback by providing additional details'
                  : regeneratedFeedback && feedback
                  ? 'Below is the revised version'
                  : 'Get content feedback by providing additional detail'
              }}
            </p>
          </div>
          <div v-if="!loadingFeedback" class="pointer" @click="toggleFeedbackModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div
          :class="loadingFeedback ? 'opaque' : ''"
          v-if="!feedback"
          class="paid-body input-width"
        >
          <label for="pt">Post Type</label>
          <input
            class="input-text"
            placeholder="(e.g., blog post, LinkedIn post, Tweet, Instagram, email, etc.)"
            type="text"
            v-model="feedbackType"
            :disabled="loadingFeedback"
            id="pt"
          />

          <label for="aud">Audience</label>
          <input
            class="input-text"
            placeholder="(e.g., age range, profession, interests, etc.)"
            type="text"
            v-model="audience"
            :disabled="loadingFeedback"
            id="aud"
          />

          <label for="po">Post Objective</label>
          <input
            class="input-text"
            placeholder="(e.g., to inform, to persuade, to entertain, etc.)"
            type="text"
            v-model="objective"
            :disabled="loadingFeedback"
            id="po"
          />

          <label for="sf">Specific feedback</label>
          <input
            class="input-text"
            placeholder="(e.g., headline effectiveness, clarity, engagement tactics, etc.)"
            type="text"
            v-model="specificFeedback"
            :disabled="loadingFeedback"
            id="sf"
          />
        </div>

        <div v-else class="paid-body">
          <pre v-html="feedback" class="pre-text" style="font-size: 14px"></pre>
        </div>

        <div class="paid-footer">
          <div class="row">
            <button
              :disabled="loadingFeedback"
              @click="toggleFeedbackModal"
              class="secondary-button"
            >
              {{ !feedback ? 'Cancel' : 'Close' }}
            </button>
            <button
              v-if="!feedback"
              @mouseenter="changeFeedbackText"
              @mouseleave="defaultFeedbackText"
              :disabled="loadingFeedback || !isPaid"
              @click="getFeedback"
              class="primary-button no-transitions"
            >
              <!-- <img
                v-if="loadingFeedback"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
              /> -->
              {{ feedbackText }}
              <div style="margin-left: 4px" v-if="loadingFeedback" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>

            <button
              :disabled="loadingFeedback || !isPaid"
              v-else-if="feedback && !regeneratedFeedback"
              @click="handleRegenerateFeedback"
              class="primary-button no-transitions"
            >
              <!-- <img
                v-if="loadingFeedback"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
              /> -->
              Apply Feedback
              <div style="margin-left: 4px" v-if="loadingFeedback" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>

            <button v-else @click="copyFeedbackText" class="primary-button no-transitions">
              {{ copyTip }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="deleteModalOpen" class="process-modal">
      <div style="width: 450px" class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="toggleDeleteModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Are you sure?</h3>
              <h5 class="regen-body-title">This process will be permanently removed.</h5>
            </div>
          </div>
        </div>
        <div style="margin-top: 32px" class="paid-footer">
          <div class="row">
            <div class="secondary-button" @click="toggleDeleteModal">Cancel</div>
            <div class="reset-button" @click="deleteProcess">Delete</div>
          </div>
        </div>
      </div>
    </Modal>

    <div class="center-left">
      <div class="full-width center">
        <div class="header">
          <div>
            <h2 class="large-text">Automate</h2>
            <p class="med-text">Streamline the entire content creation process with AI</p>
          </div>

          <div
            style="margin-bottom: 30px; padding: 0 16px"
            class="input-container"
            v-clickOutsideMenu
          >
            <div style="margin-right: -8px" class="row">
              <div v-if="!isMobile" class="main-text">Process</div>
              <input
                class="area-input"
                placeholder="Select process..."
                @focus="showDropdown"
                autocomplete="off"
                :disabled="loading || processLoading"
                v-model="processText"
              />
            </div>

            <div v-if="showingDropdown" class="dropdown">
              <div class="bottom-margin-small">
                <small class="gray-text">Select Process</small>
              </div>

              <div
                @click="startProcess(process)"
                class="dropdown-item"
                v-for="(process, i) in filteredProcesses"
                :key="i"
              >
                <p>
                  {{ process.name }}
                </p>
              </div>

              <p v-if="!processes.length" class="dropdown-item">Saved processes will appear here</p>

              <div class="dropdown-footer">
                <button :disabled="!isPaid" @click="toggleModal" class="primary-button">
                  Create new process
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="center-left-gray">
      <div class="full-width center">
        <div class="header">
          <div class="space-between bottom-margin">
            <p class="med-text top-margin">
              {{ currentProcess ? currentProcess.name : 'AI generated content will appear below' }}
            </p>

            <p v-if="generatedContent" class="med-text top-margin">
              {{ generatedContent.split(' ').length }} words
            </p>
          </div>

          <div class="space-between bottom-margin">
            <div>
              <div v-if="processLoading">
                <div class="med-text gray-span row">
                  {{ `Step ${currentStep}/3:` }}
                  <span>{{ stepName }}</span>
                  <div class="loading">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                  </div>
                </div>
              </div>

              <div v-else-if="contentLoading">
                <div class="med-text row">
                  <p style="margin-right: 0.5rem">Regenerating</p>
                  <div class="loading">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                  </div>
                </div>
              </div>

              <div
                style="margin-top: -8px"
                v-else-if="!contentLoading && !processLoading && generatedContent"
              >
                <p class="med-text gray-text">AI-generated content</p>
              </div>
            </div>

            <div style="display: flex; padding: 0 0 16px 0">
              <div style="margin-right: 0.5rem">
                <div
                  @click="toggleDeleteModal"
                  class="wrapper circle-border white-bg"
                  v-if="generatedContent"
                >
                  <img
                    style="cursor: pointer"
                    class="img-highlight"
                    src="@/assets/images/trash.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Delete</div>
                </div>
                <div v-else class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="img-highlight"
                    src="@/assets/images/trash.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Run process first</div>
                </div>
              </div>

              <div style="margin-right: 0.5rem">
                <div
                  @click="toggleFeedbackModal"
                  class="wrapper circle-border white-bg"
                  :class="{ 'bluee-bg': feedback }"
                  v-if="generatedContent"
                >
                  <img
                    style="cursor: pointer"
                    class="right-mar img-highlight"
                    src="@/assets/images/thumb.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">
                    {{ !feedback ? 'Optimize Content' : 'View Feedback' }}
                  </div>
                </div>
                <div v-else class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="right-mar img-highlight"
                    src="@/assets/images/thumb.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Run process first</div>
                </div>
              </div>

              <div style="margin-right: 0.5rem">
                <div
                  @click="toggleJournalistModal"
                  class="wrapper circle-border white-bg"
                  :class="{ 'bluee-bg': journalists }"
                  v-if="generatedContent"
                >
                  <img
                    style="cursor: pointer"
                    class="img-highlight"
                    src="@/assets/images/profile.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">
                    {{ !journalists ? 'Find Journalists' : 'View Journalists' }}
                  </div>
                </div>
                <div v-else class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="img-highlight"
                    src="@/assets/images/profile.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Run process first</div>
                </div>
              </div>

              <div>
                <div
                  @click="copyText"
                  class="wrapper circle-border white-bg"
                  v-if="generatedContent"
                >
                  <img
                    style="cursor: pointer"
                    class="img-highlight"
                    src="@/assets/images/clipboard.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">{{ copyTip }}</div>
                </div>
                <div v-else class="wrapper circle-border white-bg" style="opacity: 0.7">
                  <img
                    style="cursor: not-allowed"
                    class="img-highlight"
                    src="@/assets/images/clipboard.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -14px" class="tooltip">Run process first</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="center-left white-bg">
      <div class="full-width center">
        <div class="header">
          <pre class="pre-text top-margin" v-html="generatedContent"></pre>

          <div
            style="margin: 1rem 0; padding-top: 0; padding-bottom: 0; border-radius: 28px"
            id="instructions"
            class="input-container-chat"
            v-if="generatedContent"
          >
            <div class="row">
              <div class="main-text-img">
                <img
                  style="margin-top: 4px"
                  src="@/assets/images/comment.svg"
                  height="18px"
                  alt=""
                />
              </div>

              <textarea
                style="margin: 0; padding: 16px 24px 12px 24px"
                class="area-input text-area-input"
                id="instructions-text-area"
                placeholder="Make edits..."
                v-model="instructions"
                :rows="1"
                v-autoresize
              />

              <div @click="instructions = ''" class="cancel-container">
                <img src="@/assets/images/add.svg" class="lip-img filtered-blue" />
              </div>
              <button
                @click="regenerateContent"
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
// import User from '@/services/users/'

export default {
  name: 'Assist',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      instructions: '',
      showingDropdown: false,
      modalOpen: false,
      journalistModalOpen: false,
      feedbackModalOpen: false,
      loading: false,
      processLoading: false,
      processes: null,
      processText: '',
      processName: null,
      processSearchId: null,
      processType: null,
      processDetails: null,
      processStyle: null,
      currentProcess: null,
      dateStart: null,
      dateEnd: null,
      copyTip: 'Copy',
      generatedContent: '',
      currentStep: 0,
      stepName: 'Scanning news',
      journalists: null,
      location: null,
      beat: null,
      pubType: null,
      journalText: 'Search',
      feedback: null,
      regeneratedFeedback: false,
      loadingFeedback: false,
      feedbackType: null,
      specificFeedback: null,
      feedback: null,
      feedbackText: 'Submit',
      deleteModalOpen: false,
      contentLoading: false,
    }
  },
  async created() {
    this.getProcesses()
    const today = new Date()
    const sevenDaysAgo = new Date(today)
    sevenDaysAgo.setDate(today.getDate() - 7)
    this.dateStart = sevenDaysAgo.toISOString().split('T')[0]
    this.dateEnd = today.toISOString().split('T')[0]
  },

  methods: {
    showDropdown() {
      this.showingDropdown = true
    },
    hideDropdown() {
      this.showingDropdown = false
    },
    toggleModal() {
      this.hideDropdown()
      this.modalOpen = !this.modalOpen
    },
    toggleJournalistModal() {
      this.journalistModalOpen = !this.journalistModalOpen
    },
    toggleFeedbackModal() {
      this.feedbackModalOpen = !this.feedbackModalOpen
    },
    toggleDeleteModal() {
      this.deleteModalOpen = !this.deleteModalOpen
    },
    getSearches() {
      this.$store.dispatch('getSearches')
    },
    async getProcesses() {
      try {
        Comms.api.getProcesses().then((response) => {
          this.processes = response.results
        })
      } catch (e) {
        console.log(e)
      }
    },
    async deleteProcess() {
      try {
        Comms.api
          .deleteProcess({
            id: this.currentProcess.id,
          })
          .then(() => {
            this.$toast('Process removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
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
        this.generatedContent = ''
        this.currentProcess = null
        this.deleteModalOpen = false
        this.getProcesses()
      }
    },
    async createProcess() {
      this.loading = true
      try {
        Comms.api
          .createProcess({
            user: this.user.id,
            name: this.processName,
            search_id: this.processSearchId.id,
            type: this.processType,
            details: this.processDetails,
            style: this.processStyle.style,
          })
          .then((response) => {
            console.log('created process', response)
            this.$toast('Sucess!', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
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
        this.loading = false
        this.clearForm()
        this.getSearches()
        this.getProcesses()
      }
    },
    async runProcess(summary) {
      this.currentStep = 3
      this.stepName = 'Generating content'
      try {
        await Comms.api
          .runProcess({
            type: this.currentProcess.type,
            details: this.currentProcess.details,
            style: this.currentProcess.style,
            process_id: this.currentProcess.id,
            summary: summary,
          })
          .then((response) => {
            this.generatedContent = response.content
            this.$toast('Sucess!', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
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
        this.processLoading = false
        // this.clearForm()
      }
    },
    async startProcess(process) {
      if (this.isPaid) {
        this.generatedContent = ''
        this.currentProcess = process
        this.processLoading = true
        this.hideDropdown()
        this.currentStep = 1
        let boolean = this.searches.filter(
          (search) => search.id === this.currentProcess.search_id,
        )[0].search_boolean

        console.log('BOOLEAN : --- >', boolean)
        console.log('SEARCHES : --- >', this.searches)
        console.log('CP : --- >', this.currentProcess)

        setTimeout(() => {
          this.getClips(boolean)
        }, 1000)
      } else {
        this.$toast('Upgrade to pro!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getClips(boolean) {
      try {
        await Comms.api
          .getClips({
            boolean: boolean,
            user_id: this.user.id,
            date_to: this.dateStart,
            date_from: this.dateEnd,
          })
          .then((response) => {
            let articles = response.articles
            this.getSummary(articles)
          })
      } catch (e) {
        console.log(e)
      }
    },
    async getSummary(clips) {
      this.currentStep = 2
      this.stepName = 'Summarizing coverage'
      const allClips = this.getArticleDescriptions(clips)
      const search = this.searches.filter(
        (search) => search.id === this.currentProcess.search_id,
      )[0].input_text

      const instructions = this.searches.filter(
        (search) => search.id === this.currentProcess.search_id,
      )[0].instructions

      try {
        await Comms.api
          .getSummary({
            clips: allClips,
            search: search,
            instructions: instructions,
          })
          .then((response) => {
            this.runProcess(response.summary)
          })
      } catch (e) {
        console.log(e)
      }
    },
    getArticleDescriptions(articles) {
      return articles.map(
        (a) =>
          `Content:${a.description} Date:${a.publish_date}, Source:${a.source.name}, Author:${a.author}`,
      )
    },
    async copyText() {
      try {
        await navigator.clipboard.writeText(this.generatedContent)
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
    async copyFeedbackText() {
      try {
        await navigator.clipboard.writeText(this.feedback)
        this.copyTip = 'Copied!'
        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async getJournalists() {
      this.journalText = 'Searching'
      this.loading = true
      try {
        await Comms.api
          .getJournalists({
            type: this.pubType,
            beat: this.beat,
            location: this.location,
            content: this.generatedContent,
          })
          .then((response) => {
            this.journalists = response.journalists
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
        this.journalText = 'Search'
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
    changeFeedbackText() {
      if (!this.isPaid) {
        this.feedbackText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultFeedbackText() {
      if (!this.isPaid) {
        this.feedbackText = 'Submit'
      } else {
        return
      }
    },
    async handleRegenerateFeedback() {
      this.loadingFeedback = true
      try {
        await Comms.api
          .regenerateWithFeedback({
            content: this.generatedContent,
            feedback: this.feedback,
          })
          .then((response) => {
            this.regeneratedFeedback = true
            this.feedback = response.feedback
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingFeedback = false
      }
    },
    async getFeedback() {
      this.loadingFeedback = true
      try {
        await Comms.api
          .getFeedback({
            type: this.feedbackType,
            audience: this.audience,
            objective: this.objective,
            feedback: this.specificFeedback,
            content: this.generatedContent,
          })
          .then((response) => {
            this.feedback = response.feedback
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingFeedback = false
      }
    },
    async regenerateContent() {
      this.contentLoading = true
      const tempContent = this.generatedContent
      this.generatedContent = ''

      try {
        await Comms.api
          .regeneratePitch({
            pitch: tempContent,
            instructions: this.instructions,
          })
          .then((response) => {
            this.generatedContent = response.pitch
          })
      } catch (e) {
        console.log('ERROR CREATING content::', e)
      } finally {
        this.instructions = ''
        this.contentLoading = false
        // this.scrollToTop()
      }
    },
    clearForm() {
      this.processName = null
      this.processSearchId.id = null
      this.processType = null
      this.processDetails = null
      this.processStyle.style = null
      this.toggleModal()
    },
    testValues() {
      console.log(
        this.processName,
        this.processSearchId.id,
        this.processType,
        this.processDetails,
        this.processStyle.style,
      )
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    isMobile() {
      return window.innerWidth <= 600
    },
    searches() {
      return this.$store.state.allSearches
    },
    writingStyles() {
      return this.$store.state.user.writingStylesRef
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    filteredProcesses() {
      return this.processes.filter((process) =>
        process.name.toLowerCase().includes(this.processText.toLowerCase()),
      )
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
    clickOutsideMenu: {
      bind(el, binding, vnode) {
        function clickOutsideHandler(e) {
          if (!el.contains(e.target)) {
            vnode.context.hideDropdown()
          }
        }

        document.body.addEventListener('click', clickOutsideHandler)

        el._clickOutsideHandler = clickOutsideHandler
      },

      unbind(el) {
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

button:disabled {
  background-color: $off-white !important;
}

.grow:hover {
  transform: scale(1.2);
  box-shadow: 2px 4px 32px rgba($color: $black, $alpha: 0.3);
  opacity: 0.7;
}
.grow {
  transition: all 0.2s;
}

.faded {
  filter: invert(55%);
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

.filtered-blue {
  filter: invert(20%) sepia(28%) saturate(811%) hue-rotate(162deg) brightness(94%) contrast(81%);
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

.input-container-chat {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  width: 100%;
  background-color: $offer-white;
  color: $base-gray;
  position: relative;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}
.reset-button {
  @include white-button-danger();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  margin-left: 1rem;
}

.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

::v-deep .multiselect * {
  font-size: 14px;
  font-family: $thin-font-family;
  // border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.pointer {
  cursor: pointer;
}

.process-modal {
  margin-top: 132px;
  @media only screen and (max-width: 600px) {
    margin-top: 62px;
  }
}

.modal-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  color: $base-gray;
  font-family: $thin-font-family;
  scroll-behavior: smooth;

  label {
    font-size: 14px;
  }
  @media only screen and (max-width: 600px) {
    width: 95%;
  }
}

// .modal-container::-webkit-scrollbar {
//   width: 6px;
//   height: 0px;
//   display: none;
// }
// .modal-container::-webkit-scrollbar-thumb {
//   background-color: $soft-gray;
//   box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
//   border-radius: 6px;
// }

// .modal-container:hover::-webkit-scrollbar {
//   display: block;
// }

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
  font-size: 13px;
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

.full-width {
  width: 100vw;
  //   display: flex;
  //   align-items: center;
  //   justify-content: center;
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  position: relative;
  border-radius: 8px;
  padding: 58px 36px 0 36px;
  height: 100vh;
  width: 100vw;
  color: $dark-blue;
  background-color: white;
  overflow-y: scroll;
  font-family: $thin-font-family;
  @media only screen and (max-width: 600px) {
    padding: 12px 12px 0 12px;
  }
}

.header {
  width: 700px;
  padding: 0 1rem;
}

.center-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  background-color: $dark-black-blue;
  color: white;
}

.center-left-gray {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  background-color: $off-white;
  color: $dark-black-blue;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem;
  border-radius: 6px;
  width: 100%;
  background-color: $offer-white;
  color: $base-gray;
  position: relative;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}

.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0.75rem 1.25rem;
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

.area-input::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.area-input::placeholder {
  font-family: $thin-font-family;
}

.text-area-input {
  padding-top: 1.5rem;
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;
  margin-right: 8px;
}

.pre-text {
  border-radius: 4px;
  margin: 0;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.main-text {
  min-width: 80px !important;
  display: flex;
  flex-direction: row;
  align-items: center;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  margin: 0;
  font-size: 13px;
  color: $dark-black-blue;
  svg,
  img {
    filter: invert(40%);
    margin: 0;
    padding: 0;
  }
}

.primary-button {
  @include dark-blue-button();
  padding: 10px 12px;
  border: none;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.dropdown-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0 1rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: flex-start;
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
  z-index: 2300;

  p {
    margin: 0;
  }

  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }

  &:hover {
    opacity: 0.7;
  }
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
}

.no-transitions:hover {
  scale: 1 !important;
}

.input-text {
  width: 600px;
  margin: 1rem 0;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family !important;
  font-size: 13px;
  padding: 10px 20px 10px 18px;
  outline: none;
}

.input-width {
  input {
    width: 500px !important;
    @media only screen and (max-width: 600px) {
      width: 95% !important;
    }
  }
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
  justify-content: flex-end;
}

.gray-text {
  color: $mid-gray;
}

.med-text {
  font-size: 14px;
}

.gray-span {
  color: $mid-gray;
  span {
    color: $dark-black-blue;
    display: block;
    margin: 0 8px 0 4px;
  }
}

.large-text {
  font-size: 21px;
}

.white-bg {
  background-color: white;
  color: $dark-black-blue;
}

.space-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.top-margin {
  margin-top: 2rem;
}

.bottom-margin {
  margin-bottom: 1rem;
}

.bottom-margin-small {
  margin-bottom: 0.5rem;
}

.opaque {
  opacity: 0.75;
}

.white-bg {
  background: white;
}
.bluee-bg {
  background: $white-blue !important;
}

.circle-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 100%;
  padding: 5px 6px;

  img {
    margin: 0 !important;
  }
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

.loading {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0.75rem 0.5rem 0.5rem 0rem;
}

.loading-small {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
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
</style>