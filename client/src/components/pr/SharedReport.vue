<template>
  <div v-if="this.report" class="reports">
    <div class="pdf-slide-container">
      <img class="pdf-slide-image" :src="report.main_image" alt="Description of image" />
      <!-- <h1>{{ report.title }}</h1> -->
    </div>

    <div>
      {{ report.meta_data.summary }}
    </div>

    <section>
      <div v-for="(clip, i) in report.meta_data.clips" :key="i">
        <img :src="clip.urlToImage" height="80px" alt="" />
        <h1>{{ clip.title }}</h1>
        <p>{{ clip.description }}</p>
        <p>{{ clip.summary }}</p>
      </div>
    </section>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
import User from '@/services/users'

export default {
  name: 'SharedReport',
  data() {
    return {
      report: null,
      code: null,
      imageUrl: null,
    }
  },
  props: {
    clips: {},
  },
  async created() {
    if (this.$route.params.code) {
      let code = this.$route.params.code
      this.code = code
      try {
        await User.api.getReport(code).then((response) => {
          this.report = response
          console.log(this.report)
        })
      } catch (e) {
        console.log(e)
      }
    }
  },
  methods: {
    async getReports() {
      try {
        await User.api.getReports({ user: this.$store.state.user.id }).then((response) => {
          console.log(response)
        })
      } catch (e) {
        console.log(e)
      }
    },
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
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

.pdf-slide-container {
  width: 800px;
  height: 600px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.pdf-slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>