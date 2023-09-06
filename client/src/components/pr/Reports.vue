<template>
  <div class="reports">
    <header class="blur-bottom">
      <div>
        <h3>Share</h3>
        <small class="subtext">Customize & preview your report</small>
      </div>

      <div @click="emitReportToggle" class="report-toggle">
        <img src="@/assets/images/close.svg" height="14px" alt="" />
      </div>
    </header>
    <div class="container">
      <img v-if="imageUrl" :src="imageUrl" height="80px" alt="Uploaded Cover" class="cover-photo" />

      <div class="top-padding">
        <p v-if="!imageUrl">Cover Slide</p>
        <small v-if="!imageUrl">Add a cover slide</small>

        <input id="imageInput" class="absolute pointer" type="file" @change="test" />

        <svg class="absolute pointer" width="18" height="18">
          <path d="M9 9H3v1h6v6h1v-6h6V9h-6V3H9v6z" fill-rule="evenodd"></path>
        </svg>
      </div>
    </div>
    <div class="container medium">
      <div style="padding-bottom: 8px" class="space-between sticky-top">
        <div>
          <p>Summary</p>
          <small>AI-generated summary of the clips below</small>
        </div>

        <button @click="getSummary" :disabled="!clips.length || loading" class="secondary-button">
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
        <small v-else>
          <pre class="pre-text" v-html="summary"></pre>
        </small>
      </div>
    </div>

    <div class="container-large">
      <div class="space-between sticky-top">
        <div>
          <p>Clips</p>
          <small>Clips included in your report</small>
        </div>

        <div class="counter">{{ clips.length }}/20</div>
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
          <small>{{ clip.title }}</small>
        </div>

        <div v-if="clip.summary" class="summary-box">
          <pre v-html="clip.summary" class="pre-text-small"></pre>
        </div>

        <div
          :class="{ 'blue-bg': clip.summary }"
          v-show="currentRow === i || loadingUrl === clip.url"
          class="row absolute-right actions"
        >
          <button
            @click="getArticleSummary(clip.title, clip.url)"
            style="margin-right: 8px; padding: 6px"
            class="secondary-button blue"
            v-if="!clip.summary"
          >
            <img v-if="!summaryLoading" src="@/assets/images/sparkles-thin.svg" height="12px" />
            <img v-else class="rotate" height="12px" src="@/assets/images/loading.svg" alt="" />
          </button>
          <button v-else style="margin-right: 8px; padding: 6px" class="secondary-button blue">
            <img src="@/assets/images/expand-arrows.svg" height="12px" />
          </button>
          <button @click="removeClip(clip)" style="padding: 6px" class="secondary-button danger">
            <img src="@/assets/images/trash.svg" height="12px" />
          </button>
        </div>
      </div>
    </div>
    <footer>
      <p></p>
      <div class="row">
        <button class="secondary-button" @click="clearClips">Clear</button>
        <button style="margin-left: 16px" class="primary-button" @click="createReport">
          Preview
        </button>
      </div>
    </footer>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
import User from '@/services/users'

export default {
  name: 'Reports',
  data() {
    return {
      imageUrl: null,
      summary: '',
      searchTerm: 'Anime',
      loading: false,
      currentRow: null,
      imageFile: null,
      summaryLoading: false,
      loadingUrl: null,
    }
  },
  props: {
    clips: {},
  },
  methods: {
    // async getReports() {
    //   try {
    //     await User.api.getReports({ user: this.$store.state.user.id }).then((response) => {
    //       console.log(response)
    //     })
    //   } catch (e) {
    //     console.log(e)
    //   }
    // },
    async getArticleSummary(title, url, instructions = null, length = 500) {
      this.summaryLoading = true
      this.loadingUrl = url
      try {
        await Comms.api
          .getArticleSummary({
            url: url,
            search: '',
            instructions: instructions,
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
      let formData = new FormData()
      formData.append('title', 'JJ Kaisen')
      let imageFile = document.querySelector('#imageInput').files[0]
      if (imageFile) {
        formData.append('main_image', imageFile)
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
          console.log(response)
        })
      } catch (e) {
        console.log(e)
      }
    },
    setRow(i) {
      this.currentRow = i
    },
    removeRow() {
      this.currentRow = null
    },
    removeClip(clip) {
      console.log(clip)
      this.$emit('remove-clip', clip.title)
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
    test(event) {
      const file = event.target.files[0]
      this.imageFile = file
      console.log('IMAGE FILE', this.imageFile)
      this.createImage(file)
    },
    createImage(file) {
      const reader = new FileReader()

      reader.onload = (e) => {
        this.imageUrl = e.target.result
      }
      reader.readAsDataURL(file)
    },
    getArticleDescriptions(articles) {
      return articles.map((a) => a.content)
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
            search: this.searchTerm,
            instructions: '',
          })
          .then((response) => {
            this.summary = response.summary
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
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

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

.subtext {
  padding: 0;
}

.top-padding {
  padding-top: 16px;
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
  height: 70vh;
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

.pointer {
  cursor: pointer !important;
}
.space-between {
  display: flex;
  align-items: center;
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
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
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
  padding: 16px 0;

  button,
  p {
    margin: 0;
  }
}

.blue {
  &:hover {
    box-shadow: none;
    border: 0.7px solid $dark-black-blue;
    transform: scale(1);
    img {
      filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%)
        contrast(90%);
    }
  }
}

.danger {
  box-shadow: none !important;
  &:hover {
    border: 1px solid $coral;
    transform: scale(1);
    img {
      filter: invert(51%) sepia(74%) saturate(2430%) hue-rotate(320deg) brightness(104%)
        contrast(121%);
    }
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
</style>