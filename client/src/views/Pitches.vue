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
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
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
    <div :class="loading ? 'opaque' : 'extra-margin-top'" v-if="!pitch" class="center">
      <p v-if="!loading">Generate a pitch, blog post or press release based on any persona.</p>

      <div class="centered blue-bg" v-else>
        <div style="width: 675px" class="row">
          <p class="summary-load-text">Generating {{ type }}...</p>
        </div>

        <div class="summary-preview-skeleton shimmer">
          <div class="content">
            <div class="meta-wide"></div>
            <div class="meta-shorter"></div>
            <div class="meta-shortest"></div>
          </div>
        </div>
      </div>

      <div v-if="!user.writingStyle && !writingStyle">
        <button
          @mouseenter="changeStyleText"
          @mouseleave="defaultStyleText"
          style="margin-top: -8px; width: 280px"
          v-if="!showInput"
          @click="toggleLearnInput"
          class="primary-button extra-padding"
        >
          <img class="invert" src="@/assets/images/sparkle.svg" height="12px" alt="" />
          {{ styleText }}
        </button>

        <div v-else class="sample-row">
          <div class="input-container">
            <div class="input-row relative">
              <div class="main-text">
                <img src="@/assets/images/sparkle.svg" height="14px" alt="" />
                Sample
              </div>

              <textarea
                :disabled="savingStyle"
                maxlength="8000"
                class="area-input text-area-input"
                placeholder="Provide a sample of your writing..."
                v-model="sample"
                v-autoresize
              />

              <div class="absolute-count">
                <small>{{ remainingCharsSample }}</small>
              </div>
            </div>
          </div>

          <div class="input-row">
            <button :disabled="savingStyle" @click="toggleLearnInput" class="secondary-button">
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
              Learn
            </button>
          </div>
        </div>
      </div>

      <div style="margin-top: -1.5rem" v-else>
        <p v-if="!showInput" @click="toggleLearnInput" class="thin-font row pointer img-margin">
          <img class="green-filter" src="@/assets/images/check.svg" height="12px" alt="" />
          Trained on your writing style
          <img src="@/assets/images/pencil.svg" height="10px" alt="" />
        </p>

        <div v-else class="sample-row">
          <div class="input-container">
            <div class="input-row relative">
              <div class="main-text">
                <img src="@/assets/images/sparkle.svg" height="14px" alt="" />
                Sample
              </div>

              <textarea
                :disabled="savingStyle"
                maxlength="8000"
                class="area-input text-area-input"
                placeholder="Provide a sample of your writing..."
                v-model="sample"
                v-autoresize
              />

              <div class="absolute-count">
                <small>{{ remainingCharsSample }}</small>
              </div>
            </div>
          </div>

          <div class="input-row">
            <button :disabled="savingStyle" @click="toggleLearnInput" class="secondary-button">
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
              Learn
            </button>
          </div>
        </div>
      </div>

      <div class="input-container" v-clickOutsideInstructionsMenu>
        <div class="input-row relative">
          <div class="main-text">
            <img src="@/assets/images/wand.svg" height="14px" alt="" />
            Instructions
          </div>

          <textarea
            :disabled="loading"
            maxlength="1000"
            class="area-input text-area-input"
            :placeholder="instructionsPlaceholder"
            v-model="output"
            v-autoresize
            @focus="showInstructionsDropdown($event)"
          />

          <div class="absolute-count">
            <small>{{ remainingChars }}</small>
          </div>
        </div>
        <div v-if="showingInstructionsDropdown" class="dropdown">
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

      <div class="divider">
        <p class="divider-text">
          {{ 'Optional' }}
        </p>
      </div>

      <div class="input-container mar-top" v-clickOutsideTypeMenu>
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/document.svg" height="14px" alt="" />
            Type
          </div>

          <input
            :disabled="loading"
            class="area-input"
            placeholder="Optional"
            v-model="type"
            @focus="showTypeDropdown"
          />
        </div>
        <div v-if="showingTypeDropdown" class="dropdown">
          <small style="padding-top: 8px" class="gray-text">Example Type</small>
          <div
            @click="addTypeSuggestion(suggestion)"
            class="dropdown-item"
            v-for="(suggestion, i) in filteredTypeSuggestions"
            :key="i"
          >
            <p>
              {{ suggestion }}
            </p>
          </div>
        </div>
      </div>

      <div class="input-container" v-clickOutsideAudienceMenu>
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/target.svg" height="14px" alt="" />
            Audience
          </div>

          <input
            :disabled="loading"
            class="area-input"
            placeholder="Optional"
            v-model="persona"
            @focus="showAudienceDropdown"
          />
        </div>
        <div v-if="showingAudienceDropdown" class="dropdown">
          <small style="padding-top: 8px" class="gray-text">Example Audience</small>
          <div
            @click="addAudienceSuggestion(suggestion)"
            class="dropdown-item"
            v-for="(suggestion, i) in filteredAudienceSuggestions"
            :key="i"
          >
            <p>
              {{ suggestion }}
            </p>
          </div>
        </div>
      </div>

      <div class="input-container" v-clickOutsideBriefingMenu>
        <div class="input-row relative">
          <div class="main-text">
            <img src="@/assets/images/file-word.svg" height="14px" alt="" />
            Content
          </div>

          <textarea
            :disabled="loading"
            maxlength="1500"
            class="area-input text-area-input"
            :placeholder="optionalPlaceholder"
            v-model="briefing"
            v-autoresize
            @focus="showBriefingDropdown($event)"
          />

          <div class="absolute-count">
            <small>{{ remainingCharsBrief }}</small>
          </div>
        </div>
        <div v-if="showingBriefingDropdown" class="dropdown">
          <small style="padding-top: 8px" class="gray-text">Example Content</small>
          <div
            @click="addBriefingSuggestion(suggestion)"
            class="dropdown-item"
            v-for="(suggestion, i) in filteredBriefingSuggestions"
            :key="i"
          >
            <p>
              {{ suggestion }}
            </p>
          </div>
        </div>
      </div>

      <!-- <div class="input-container">
        <div class="input-row relative">
          <div class="main-text">
            <img src="@/assets/images/note.svg" height="14px" alt="" />
            Style
          </div>

          <textarea
            :disabled="loading"
            autofocus
            maxlength="1000"
            class="area-input"
            placeholder="Provide a sample of your writing style..."
            v-model="sample"
            v-autoresize
          />

          <div class="absolute-count">
            <small>{{ remainingChars }}</small>
          </div>
        </div>
      </div> -->

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
      </footer>
    </div>

    <div v-else class="center">
      <div class="pitch-container">
        <Transition name="slide-fade">
          <div v-if="showUpdateBanner" class="templates">
            <p>Search saved successfully!</p>
          </div>
        </Transition>
        <div class="title-container">
          <div @click="resetSearch" class="back">
            <img src="@/assets/images/back.svg" height="18px" width="18px" alt="" />
          </div>
          <h1 class="no-text-margin">{{ type }}</h1>
          <p class="sub-text">
            Target Audience: <span>{{ persona }}</span>
          </p>
        </div>

        <div class="title-bar">
          <div v-if="!showSaveName" class="row">
            <button
              :disabled="loading"
              @click="toggleRegenerate"
              v-if="!regenerating"
              class="secondary-button"
            >
              <img
                v-if="loading"
                class="rotate"
                height="14px"
                src="@/assets/images/loading.svg"
                alt=""
              />
              {{ loading ? 'Regenerating' : 'Regenerate' }}
            </button>
            <div style="width: 600px" class="row" v-else>
              <input
                :disabled="loading"
                placeholder="provide instructions..."
                autofocus
                class="regen-input"
                type="textarea"
                v-model="instructions"
              />

              <button @click="regeneratePitch" class="primary-button">Regenerate</button>
            </div>
            <div class="save-wrapper" v-if="!loading && !savingPitch && !pitchSaved">
              <button
                @click="toggleSaveName"
                v-if="!regenerating"
                :disabled="loading || savingPitch || pitchSaved"
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
              <div style="margin-left: -50px" class="save-tooltip">Save this version</div>
            </div>
            <div v-else>
              <button
                @click="toggleSaveName"
                v-if="!regenerating"
                :disabled="loading || savingPitch || pitchSaved"
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
            </div>
          </div>

          <div v-else class="row">
            <input
              autofocus
              class="area-input-outline"
              placeholder="Name your pitch"
              v-model="pitchName"
            />

            <button
              @click="createSavedPitch"
              :disabled="loading || savingPitch || pitchSaved"
              class="primary-button"
            >
              Save
            </button>
          </div>

          <div @click="copyText" v-if="true /*!regenerating*/" class="wrapper circle-border">
            <img
              style="cursor: pointer"
              class="right-mar img-highlight"
              src="@/assets/images/clipboard.svg"
              height="12px"
              alt=""
            />
            <div style="margin-left: -14px" class="tooltip">{{ copyTip }}</div>
          </div>
        </div>

        <pre v-html="pitch" class="pre-text"></pre>
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
      styleText: 'Personalized AI: Learn my writing style',
      type: '',
      output: '',
      persona: '',
      briefing: '',
      pitch: null,
      loading: false,
      regenerating: false,
      paidModal: false,
      showingTypeDropdown: false,
      showingAudienceDropdown: false,
      showingBriefingDropdown: false,
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
      briefingSuggestions: [
        `XXX is launching a ...`,
        `XXX's professor, an expert in ...`,
        `Call summary: XXX ...`,
        `Email exchange: XXX ...`,
      ],
      instructionsSuggestions: [
        `A concise blog post targeting millennial moms about ...`,
        `Media pitch, concise, on behalf of XXX, tailored to a tech beat writer at the NYTs about ...`,
        `Mirror my writing style: {insert a paragraph of your writing}`,
        `Press release, highly persuasive about the launch of XXX's new product ...`,
        `An entertaining tweet about XXX catered to Gen X ...`,
        `A short, casual, direct follow up email to Susan, the VP of Marketing at XXX ...`,
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
    }
  },
  watch: {
    currentPitch(newVal, oldVal) {
      if (newVal.id !== (oldVal ? oldVal.id : null)) {
        this.setPitch(newVal)
      }
    },
  },
  created() {
    if (this.$store.state.generatedContent) {
      this.briefing = this.$store.state.generatedContent.summary
        .split('<strong>')
        .filter((item) => item !== '<strong>')
        .join('')
        .split('</strong>')
        .filter((item) => item !== '</strong>')
        .join('')
      this.output = `Create a ${
        this.$store.state.generatedContent.type + ` for ` + this.$store.state.generatedContent.term
      }`
      this.type = this.$store.state.generatedContent.type
    }
  },
  beforeDestroy() {
    this.$store.commit('setGeneratedContent', null)
  },
  methods: {
    test() {
      console.log(this.user)
    },
    async saveWritingStyle() {
      this.savingStyle = true
      try {
        await Comms.api
          .saveWritingStyle({
            example: this.sample,
          })
          .then((response) => {
            console.log(response.style)
            this.writingStyle = response.style
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.sample = ''
        this.toggleLearnInput()
        this.savingStyle = false
        this.refreshUser()
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
        this.styleText = 'Personalized AI: Learn my writing style'
      } else {
        return
      }
    },
    toggleLearnInput() {
      if (this.isPaid) {
        this.showInput = !this.showInput
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
    toggleSaveName() {
      this.showSaveName = !this.showSaveName
    },
    resetSearch() {
      this.pitch = null
      this.type = ''
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
    showBriefingDropdown(e) {
      // this.storedEvent = e
      // this.storedPlaceholder = e.target.placeholder
      // e.target.placeholder = ''
      this.optionalPlaceholder = ''
      this.showingBriefingDropdown = true
    },
    hideBriefingDropdown() {
      this.optionalPlaceholder = 'Optional'
      // this.storedEvent.target.placeholder = this.storedPlaceholder
      // this.storedPlaceholder = ''
      this.showingBriefingDropdown = false
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
    addTypeSuggestion(ex) {
      this.type = ex
      this.hideTypeDropdown()
    },
    addAudienceSuggestion(ex) {
      this.persona = ex
      this.hideAudienceDropdown()
    },
    addBriefingSuggestion(ex) {
      this.briefing = ex
      this.hideBriefingDropdown()
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
          content: this.briefing,
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
            content: this.briefing,
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
      this.loading = true
      try {
        await Comms.api
          .regeneratePitch({
            pitch: this.pitch,
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
        this.loading = false
        this.scrollToTop()
      }
    },
    async generatePitch() {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal()
        return
      }
      this.loading = true
      try {
        await Comms.api
          .generatePitch({
            type: this.type,
            instructions: this.output,
            audience: this.persona,
            content: this.briefing,
            style: this.user.writingStyle || this.writingStyle,
          })
          .then((response) => {
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
      this.briefing = pitch.content
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
    },
  },
  computed: {
    remainingChars() {
      return 1000 - this.output.length
    },
    remainingCharsBrief() {
      return 1500 - this.briefing.length
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
    filteredBriefingSuggestions() {
      if (!this.briefing) return this.briefingSuggestions
      return this.briefingSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.briefing.toLowerCase()),
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
    clickOutsideBriefingMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideBriefingDropdown()
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
  bottom: -2px;
  right: -8px;
  font-size: 11px;
  color: $light-gray-blue;
  background-color: white;
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

.sub-text {
  color: $light-gray-blue;
  margin: 8px 0 0 0;
  font-size: 14px;
  font-weight: bold;
  font-family: $thin-font-family;
  span {
    font-weight: normal;
    word-wrap: break-word;
  }
}

.title-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 24px 0 24px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
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
  padding-top: 48px;
  width: 50%;
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
  background-color: $white-blue;
  border-radius: 4px;
  padding: 16px;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.pitches {
  background-color: white;
  width: 100vw;
  height: 100vh;
  padding: 0 36px 0 36px;
  display: flex;
  overflow-y: scroll;
  font-family: $base-font-family;
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
  height: 100%;
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
  padding: 0.75rem 1.2rem 0.75rem 1.2rem;
  border-radius: 6px;
  width: 675px;
  background-color: $offer-white;
  color: $base-gray;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
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
  font-family: $base-font-family;
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

.blue-bg {
  padding-top: 66px;
  background-color: $white-blue;
}

.opaque {
  opacity: 0.75;
  padding-top: 0 !important;
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
  width: 675px;
  // min-width: 400px;
  padding: 8px 20px 16px 0;
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
}
.paid-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
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
}
.regen-body-title {
  margin: 0 0 0 0;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
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
  padding: 8px 0 8px 0;
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
.gray-text {
  color: $mid-gray;
}
.mar-top {
  margin-top: 1rem;
}
.text-area-input::placeholder {
  padding-top: 1rem;
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
</style>