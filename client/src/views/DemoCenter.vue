<template>
    <div class="demo-center-container">
        <div style="margin-bottom: 8rem;">
            <h2 class="page-title">Demo Center</h2>
            <p class="page-subtitle">Learn more about how Managr helps sellers work faster and more efficiently.</p>
        </div>
        <div class="video-section-container">
            <VideoSection 
                title="Managr 101: Getting Started"
                :videoURL="require('../assets/videos/getting-started.mp4')"
                boldSubtitle="Onboard in less than 5 minutes."
                subtitle="Connect your CRM, Slack, Calendar, and start automating busy work."
                class="video-width"
            />
            <VideoSection 
                title="Slack Commands & Chatbot"
                :videoURL="require('../assets/videos/slack-commands-and-chatbot.mp4')"
                boldSubtitle="Use Slack commands"
                subtitle="to take action from anywhere in Slack. Update & create CRM records in seconds via chat."
                class="video-width"
            />
            <VideoSection 
                title="Generate Content using AI"
                :videoURL="require('../assets/videos/generate-content.mp4')"
                boldSubtitle="Turn your updates into content."
                subtitle="Draft follow up emails, summarize mettings, and get next steps using AI."
                class="video-width"
            />
        </div>
    </div>
</template>

<script>
// import AlertTemplate from '@/services/alerts/'
import VideoSection from '../components/VideoSection.vue';

export default {
    name: 'DemoCenter',
    components: {
        VideoSection,
    },
    data() {
        return {
            default: null,
        }
    },
    created() {

    },
    methods: {

    },
    computed: {

    },
}
</script>

<style lang="scss" scoped>


.demo-center-container {
    margin-left: 60px; 
    background-color: white;
    padding: 1rem;
    margin-top: 0.5rem;
    height: 91.25vh;
}
.video-section-container {
    display: flex;
    justify-content: space-between;
}
.page-title {
    font-size: 3rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.page-subtitle {
    font-size: 1.2rem;
}
.video-width {
    width: 25vw;
}
video {
    object-fit: fill;
}
</style>