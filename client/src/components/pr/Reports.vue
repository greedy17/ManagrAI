<template>
  <div class="reports">
    <header class="blur-bottom">
      <div>
        <h3>{{ reportSuccess ? 'Successfully created digest!' : 'Digest' }}</h3>
        <small class="subtext">{{
          reportSuccess ? 'Below is your shareable link' : 'Create a sharable media digest'
        }}</small>
      </div>

      <div @click="emitReportToggle" class="report-toggle">
        <img src="@/assets/images/close.svg" height="14px" alt="" />
      </div>
    </header>

    <div style="margin-top: 16px" v-if="reportSuccess">
      <div class="container small">
        <div class="top-padding ellipsis-text">
          <small>{{ reportLink }}</small>
        </div>
      </div>

      <section class="row">
        <div class="wrapper">
          <button @click="copyText" style="margin-left: 2px" class="secondary-button">
            Copy link
          </button>

          <div class="tooltip">{{ copyTip }}</div>
        </div>
        <button @click="openLink" style="margin-left: 8px" class="primary-button">
          <img src="@/assets/images/openwindow.svg" height="12px" alt="" />
          Open
        </button>
      </section>

      <div class="divider"></div>

      <small class="subtext med-text">
        Access previously created reports <a @click="goToReports">here</a>
      </small>
    </div>

    <div v-else>
      <div :class="{ dull: reportLoading }" class="container">
        <img
          accept=".jpg, .jpeg, .png, .gif, .bmp, .tiff, .tif, .webp"
          style="margin-top: 8px"
          v-if="imageUrl"
          :src="imageUrl"
          alt="Uploaded Cover"
          class="cover-photo"
        />
        <input v-if="imageUrl" id="imageInput" class="absolute-button-input-large pointer dull" type="file" @change="getImage" />
        <input v-else-if="!imageUrl" id="imageInput" class="absolute-button-input-less-large pointer dull" type="file" @change="getImage" />
        
        <div class="top-padding">
          <div class="space-between">
            <div>
              <p v-if="!imageUrl">Cover Slide</p>
              <small v-if="!imageUrl">Add title and cover image</small>
            </div>
            <button
              v-if="!imageUrl"
              class="secondary-button"
            >
              <input id="imageInput" class="absolute-button-input pointer dull" type="file" @change="getImage" />
              <span class="pointer">Add Image</span>
            </button>
          </div>

          <!-- <svg class="absolute pointer" width="18" height="18">
            <path d="M9 9H3v1h6v6h1v-6h6V9h-6V3H9v6z" fill-rule="evenodd"></path>
          </svg> -->
        </div>
        <!-- @mouseenter="isHovering" @mouseleave="notHovering"  -->
        <div class="report-name">
          <div class="relative row">
            <input
              :disabled="reportLoading"
              class="text-input no-margin"
              placeholder="Report Title..."
              autofocus
              @blur="showTitleSave"
              v-model="reportTitle"
              @input="handleReportTitleInput"
              type="text"
            />
            <!-- <button style="margin-left: 8px" class="secondary-button">save</button> -->
          </div>
        </div>
      </div>
      <div :class="{ dull: reportLoading }" class="container medium">
        <div style="padding-bottom: 8px" class="space-between sticky-top">
          <div>
            <p>Summary</p>
            <small>Generate a summary of the clips below</small>
          </div>

          <button
            v-if="!summary"
            @click="getSummary"
            :disabled="!clips.length || loading || summaryLoading"
            class="secondary-button"
          >
            Generate
          </button>
        </div>

        <div class="summary-body">
          <div class="loader-container" v-if="loading">
            <div class="loading">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
          <small class="pointer" v-else-if="summary">
            <pre
              ref="editablePre"
              @input="updateSummary"
              contenteditable="true"
              class="pre-text cursor"
              v-html="summary"
              :disabled="reportLoading"
            ></pre>
          </small>

          <div v-else>
            <!-- <input
            :disabled="!clips.length || loading || summaryLoading"
            class="text-input"
            placeholder="Search term..."
            type="text"
            v-model="searchTerm"
          /> -->
            <textarea
              :disabled="!clips.length || loading || summaryLoading || reportLoading"
              v-autoresize
              class="area-input"
              placeholder="Summary instructions (optional)..."
              v-model="instructions"
            ></textarea>
          </div>
        </div>
      </div>

      <div :class="{ dull: reportLoading }" class="container-large">
        <div class="space-between sticky-top">
          <div>
            <p>Clips</p>
            <small>Articles included in your report</small>
          </div>

          <div style="margin-top: 8px" class="row">
            <!-- <svg style="margin-right: 16px" width="16" height="16">
              <path d="M9 9H3v1h6v6h1v-6h6V9h-6V3H9v6z" fill-rule="evenodd"></path>
            </svg> -->
            <div class="counter">{{ clips.length }}/20</div>
          </div>
        </div>

        <div
          @mouseenter="setRow(i)"
          @mouseleave="removeRow"
          class="clip"
          :class="{ 'blue-bg': clip.summary }"
          v-for="(clip, i) in clips"
          :key="i"
        >
          <div class="clip-header">
            <img :src="clip.urlToImage" class="clip-photo" />
            <small>{{ clip.title ? clip.title : clip.text }}</small>
          </div>

          <div v-if="clip.summary" class="summary-box">
            <pre v-html="clip.summary" class="pre-text-small"></pre>
          </div>

          <div
            :class="{ 'blue-bg': clip.summary }"
            v-show="currentRow === i || loadingUrl === clip.url"
            class="row absolute-right actions"
          >
            <img
              @click="getArticleSummary(clip.title, clip.url, clip.search)"
              style="margin-right: 12px"
              class="blue"
              v-if="!summaryLoading && !clip.summary && clip.title"
              v-show="!clip.summary && !loading && !summaryLoading && !reportLoading"
              src="@/assets/images/sparkles-thin.svg"
              height="16px"
            />

            <img
              style="margin-right: 12px"
              v-else-if="loadingUrl === clip.url && clip.title"
              class="rotate"
              height="16px"
              src="@/assets/images/loading.svg"
              alt=""
            />

            <img
              @click="removeClip(clip)"
              class="danger"
              src="@/assets/images/trash.svg"
              height="16px"
            />
          </div>
        </div>
      </div>

      <div class="container-small">
        <div class="sticky-top">
          <div>
            <p>Add Article</p>
            <small>Paste article url below</small>
          </div>
        </div>

        <Transition name="slide-fade">
          <div v-if="showArticleBanner" :class="{ greenTemplates: success, templates: !success }">
            <p>{{ articleBannerText }}</p>
          </div>
        </Transition>
        <div style="margin-top: 16px" class="row">
          <input
            v-model="uploadLink"
            placeholder="Article URL.."
            class="text-input"
            type="text"
            style="border: 1px solid rgba(0, 0, 0, 0.1); margin-top: 8px; width: 200px"
          />
          <button
            style="margin-bottom: 6px; margin-left: 8px"
            :disabled="!uploadLink || clipLoading"
            class="primary-button"
            @click="uploadArticle"
          >
            <img
              style="margin-right: 4px"
              v-if="clipLoading"
              class="rotate"
              height="16px"
              src="@/assets/images/loading.svg"
              alt=""
            />
            {{ clipLoading ? 'Adding' : 'Add' }}
          </button>
        </div>
      </div>

      <footer>
        <p></p>
        <div class="row">
          <button
            :disabled="!clips.length || reportLoading"
            class="secondary-button"
            @click="clearClips"
          >
            Clear
          </button>
          <button
            :disabled="!clips.length || !summary || !imageUrl || !reportTitle || reportLoading"
            style="margin-left: 16px"
            class="primary-button"
            @click="createReport"
          >
            Create Report
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
import User from '@/services/users'
import debounce from 'lodash.debounce'

export default {
  name: 'Reports',
  data() {
    return {
      imageUrl: null,
      summary: '',
      searchTerm: '',
      reportTitle: '',
      loading: false,
      currentRow: null,
      imageFile: null,
      summaryLoading: false,
      clipLoading: false,
      loadingUrl: null,
      reportLoading: false,
      instructions: null,
      editingTitle: false,
      hovering: false,
      showTooltip: false,
      reportSuccess: false,
      reportLink: '',
      copyTip: 'Copy',
      uploadLink: null,
      showArticleBanner: false,
      articleBannerText: '',
      success: true,
    }
  },

  props: {
    clips: {},
    defaultSearch: {},
  },
  created() {
    this.reportTitle = this.$store.state.reportTitle
    this.imageFile = this.$store.state.reportImage
    this.summary = this.$store.state.reportSummary
  },
  methods: {
    async uploadArticle() {
      this.clipLoading = true
      try {
        await Comms.api
          .uploadLink({
            url: this.uploadLink,
          })
          .then((response) => {
            console.log('manual', response)
            this.success = true
            this.addClip(response)
            this.articleBanner('Article added!')
          })
      } catch (e) {
        this.success = false
        console.log(e)
        this.articleBanner('Error adding article!')
      } finally {
        this.clipLoading = false
        this.uploadLink = null
      }
    },
    handleDebounce: debounce((reportTitle, dispatch) => {
      dispatch('updateReportTitle', reportTitle)
    }, 900),
    articleBanner(text) {
      this.articleBannerText = text
      this.showArticleBanner = true
      setTimeout(() => {
        this.showArticleBanner = false
      }, 2000)
    },
    handleReportTitleInput() {
      this.handleDebounce(this.reportTitle, this.$store.dispatch)
    },
    addClip(clip) {
      this.$emit('add-clip', clip)
    },
    goToReports() {
      this.$router.push({
        name: 'PRReports',
      })
    },
    openLink() {
      window.open(this.reportLink, '_blank')
    },
    async copyText() {
      try {
        await navigator.clipboard.writeText(this.reportLink)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          // this.activationLink = ''
          this.copyTip = 'Copy link'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    showTitleSave() {
      this.showTooltip = true
      setTimeout(() => {
        this.showTooltip = false
      }, 1000)
    },
    updateSummary() {
      let selection = window.getSelection()
      let range = selection.getRangeAt(0)
      let position = range.startOffset

      this.summary = this.$refs.editablePre.textContent

      this.$nextTick(() => {
        let newRange = document.createRange()
        let selection = window.getSelection()
        newRange.setStart(this.$refs.editablePre.firstChild, position)
        newRange.collapse(true)
        selection.removeAllRanges()
        selection.addRange(newRange)
      })
    },
    isHovering() {
      this.hovering = true
    },
    notHovering() {
      this.hovering = false
    },
    toggleTitleEdit() {
      this.editingTitle = !this.editingTitle
    },
    async getReports() {
      try {
        await User.api.getReports({ user: this.$store.state.user.id }).then((response) => {
          this.reportLink = response.results[0]['share_url']
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.reportSuccess = true
        this.summary = null
        this.imageUrl = null
        this.clearClips()
        this.$store.dispatch('updateReportTitle', null)
        this.$store.dispatch('updateReportImage', null)
        this.$store.dispatch('updateReportSummary', null)
      }
    },
    async getArticleSummary(title, url, search, length = 500) {
      this.summaryLoading = true
      this.loadingUrl = url
      try {
        await Comms.api
          .getArticleSummary({
            url: url,
            search: search,
            instructions: '',
            length: length,
          })
          .then((response) => {
            this.$emit('edit-clip', title, response.summary)
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.summaryLoading = false
        this.loadingUrl = null
      }
    },
    async createReport() {
      this.reportLoading = true
      let formData = new FormData()
      formData.append('title', this.reportTitle)
      // let imageFile = document.querySelector('#imageInput').files[0]
      if (this.imageFile) {
        formData.append('main_image', this.imageFile)
      }
      formData.append('user', this.$store.state.user.id)
      formData.append(
        'meta_data',
        JSON.stringify({
          clips: this.clips,
          summary: this.summary,
        }),
      )
      try {
        await User.api.createReport(formData).then((response) => {
          this.getReports()
        })
        localStorage.addedClips = null
      } catch (e) {
        console.log(e)
      } finally {
        this.reportLoading = false
      }
    },
    setRow(i) {
      this.currentRow = i
    },
    removeRow() {
      this.currentRow = null
    },
    removeClip(clip) {
      this.$emit('remove-clip', clip.title ? clip.title : clip.text)
    },
    summarizeClip(clip) {
      this.$emit(
        'edit-clip',
        clip.title,
        'This is a test not the real summary. Lorem ipsum placeholder text i need to test the elippsis for longer summaries. Wondering if users should be able to regenerate here as well or if that would be too much ?',
      )
    },
    emitReportToggle() {
      this.$emit('toggle-report')
    },
    getImage(event) {
      const file = event.target.files[0]
      this.imageFile = file
      this.createImage(file)
      this.$store.dispatch('updateReportImage', file)
    },
    createImage(file) {
      const reader = new FileReader()

      reader.onload = (e) => {
        this.imageUrl = e.target.result
      }
      reader.readAsDataURL(file)
    },
    getArticleDescriptions(articles) {
      return articles.map((a) => (a.description ? a.description : a.text))
    },
    clearClips() {
      this.$emit('clear-clips')
    },
    async getSummary() {
      const allClips = this.getArticleDescriptions(this.clips)
      this.loading = true
      try {
        await Comms.api
          .getSummary({
            clips: allClips,
            search: '',
            instructions: this.instructions,
          })
          .then((response) => {
            this.summary = response.summary
            this.$store.dispatch('updateReportSummary', this.summary)
          })
      } catch (e) {
        console.log('Error in getSummary', e)
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loading = false
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
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

pre[contenteditable]:focus {
  border: none;
  outline: none;
}

.reports {
  width: 500px;
  height: 100vh;
  overflow-y: auto;
  font-family: $thin-font-family;
  padding: 0 8px 0 16px;
  background-color: $offer-white;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
  position: fixed;
  z-index: 3000;
  right: 0;
  top: 0;
  box-shadow: 30px 30px 40px;
  @media only screen and (max-width: 600px) {
    width: 100vw;
  }
}
.plus-input {
  @media only screen and (max-width: 600px) {
    width: 2rem;
  }
}
.reports::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}

.reports::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.reports:hover::-webkit-scrollbar-thumb {
  background-color: $mid-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.report-toggle {
  width: 24px;
  height: 24px;
  border-radius: 100%;
  background-color: $white-blue;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  img {
    filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
      contrast(90%);
    margin: 0;
    padding: 0;
  }
}

header {
  position: sticky;
  top: 0;
  z-index: 3300;
  background-color: $offer-white;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 4px;
}

h3 {
  margin-bottom: 0;
}

::placeholder {
  font-weight: 400;
  font-family: $thin-font-family;
}

.subtext {
  padding: 0;
}

.top-padding {
  padding-top: 16px;
  z-index: 4000;
}

.container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  padding: 0 16px 16px 16px;
  margin: 16px 0;
  border-radius: 4px;
  height: 28vh;
  position: relative;

  p {
    margin: 0;
    padding: 0;
    font-size: 14px;
  }

  small {
    color: $mid-gray;
    font-size: 12px;
  }
}

.medium {
  height: 36vh;
}

.small {
  height: 10vh;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;

  img:last-of-type {
    filter: invert(40%);
    cursor: pointer;
  }

  img:last-of-type {
    filter: invert(60%);
  }
}

.container-large {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  padding: 0 16px 16px 16px;
  margin: 16px 0;
  border-radius: 4px;
  height: 40vh;
  position: relative;
  overflow-y: scroll;

  p {
    margin: 0;
    padding: 0;
    font-size: 14px;
  }

  small {
    color: $mid-gray;
    font-size: 12px;
  }
}

.container-small {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  padding: 0 16px 16px 16px;
  margin: 16px 0;
  border-radius: 4px;
  height: 150px;
  position: relative;
  overflow-y: scroll;

  p {
    margin: 0;
    padding: 0;
    font-size: 14px;
  }

  small {
    color: $mid-gray;
    font-size: 12px;
  }
}

.sticky-top {
  background-color: white;
  position: sticky;
  top: 0;
  padding-top: 16px;
  z-index: 3250;
}

.absolute {
  position: absolute;
  top: 13vh;
  left: 220px;
}

.absolute-button-input {
  position: absolute;
  // top: 2vh;
  // top: 0;
  // left: 240px;
  height: 2rem;
  width: 5.5rem;
  z-index: 5000;
}
.absolute-button-input-large {
  position: absolute;
  // top: 2vh;
  top: 8px;
  left: 20px;
  height: 13.25rem;
  width: 27rem;
  z-index: 30;
  @media only screen and (max-width: 600px) {
    height: 10.5rem;
    width: 19.25rem;
  }
}
.absolute-button-input-less-large {
  position: absolute;
  // top: 2vh;
  top: 48px;
  left: 20px;
  height: 10rem;
  width: 27rem;
  z-index: 30;
  @media only screen and (max-width: 600px) {
    height: 10.5rem;
    width: 19.25rem;
  }
}

.pointer {
  cursor: pointer !important;
}
.space-between {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.counter {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  background-color: $white-blue;
}

.clip {
  margin: 16px 0;
  padding: 4px 0;
  border-radius: 4px;
  position: relative;
}

.absolute-right {
  position: absolute;
  right: 0;
  top: 0;
  z-index: 3200;
  padding: 8px;

  img:first-of-type {
    padding: 0;
    margin: 0;
  }
}

.clip-header {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  small {
    color: $dark-black-blue !important;
  }

  &:hover {
    opacity: 0.7;
  }
}

.clip-photo {
  height: 32px;
  width: 32px;
  object-fit: cover;
  cursor: text;
  margin-right: 8px;

  &:hover {
    opacity: 0.7;
  }
}

.cover-photo {
  height: 100%;
  width: 100%;
  object-fit: cover;
  cursor: text;

  &:hover {
    opacity: 0.7;
  }
}

.primary-button {
  @include dark-blue-button();
  padding: 8px;
  border: none;
  img {
    filter: invert(100%) !important;
    margin-right: 8px;
  }
}

.secondary-button {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  background-color: white;
  padding: 8px 12px;
  img {
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin: 0;
    padding: 0;
  }
}

input[type='file'] {
  opacity: 0;
  z-index: 3050;
}

.pre-text {
  color: $dark-black-blue;
  font-family: $thin-font-family;
  font-size: 12px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
}

.pre-text-small {
  color: $mid-gray;
  font-family: $thin-font-family;
  font-size: 12px;
  line-height: 32px;
  width: 450px;
  word-wrap: break-word;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0;
}

.summary-body {
  height: 80%;
  overflow-y: auto;
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

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 24px 8px;
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

.actions {
  background-color: white;
}

footer {
  position: sticky;
  bottom: 0;
  z-index: 3250;
  background-color: $offer-white;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 16px 8px;

  button,
  p {
    margin: 0;
  }
  @media only screen and (max-width: 600px) {
    padding: 16px 8px 48px 8px;
  }
}

.blue {
  cursor: pointer;
  &:hover {
    opacity: 0.7;
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
  }
}

.danger {
  cursor: pointer;
  &:hover {
    opacity: 0.7 !important;
    filter: invert(51%) sepia(74%) saturate(2430%) hue-rotate(320deg) brightness(104%)
      contrast(121%) !important;
  }
}

.blue-bg {
  background-color: $white-blue;
  padding-left: 4px;
}
.summary-box {
  height: 30px;
  width: 425px;
  display: flex;
  align-items: center;
  justify-content: flex-start;

  p {
    margin: 0;
    padding: 0;
    font-size: 11px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: $mid-gray;
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

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;
}

.text-input {
  width: 100%;
  margin-bottom: 16px;
  outline: none;
  background-color: $offer-white;
  border: none;
  border-radius: 4px;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $base-font-family;
  font-weight: 400;
  color: $dark-black-blue;
  padding: 0.475rem 1rem;
  z-index: 50;
}

.area-input {
  width: 100%;
  margin-bottom: 0.25rem;
  max-height: 100px;
  padding: 0.5rem 1rem;
  line-height: 1.75;
  outline: none;
  background-color: $offer-white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $base-font-family;
  font-weight: 400;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.report-name {
  max-width: 300px;
  position: absolute;
  bottom: 16px;
  left: 0;
  padding: 2px 8px;
  border-radius: 5px;
  z-index: 5000;
  background-color: white;
}

.relative {
  position: relative;
}

.abs-input-img {
  position: absolute;
  right: 12px;
  top: 10px;
  z-index: 10;
  padding-left: 8px;
  background-color: white;
  opacity: 0.7;
  cursor: pointer;
}

.no-margin {
  margin: 0 !important;
}

.centered {
  display: flex;
  align-items: center !important;
  justify-content: center !important;
}

.dull {
  opacity: 0.5;
}

.more-z {
  z-index: 5050;
}

.invert {
  filter: invert(40%);
}

.green-filter {
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
}

.med-text {
  font-size: 14px;
}

.divider {
  margin: 32px 0;
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

a {
  font-family: $base-font-family;
  color: $dark-black-blue;
  text-decoration-color: $dark-black-blue;
  font-weight: 900;
  cursor: pointer;
  text-decoration: underline;
}

.wrapper {
  display: flex;
  align-items: center;
  // background-color: ;
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
  left: -8px;
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

.ellipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  top: 32px;
  left: 16px;
  font-size: 12px;
  background: $coral;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 5000;

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
  background: $coral;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.greenTemplates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: 32px;
  left: 16px;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 5000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.greenTemplates::before {
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
.space-between {
  display: flex;
  justify-content: space-between;
}
.no-hover:hover {
  scale: 1;
  box-shadow: none;
}
</style>