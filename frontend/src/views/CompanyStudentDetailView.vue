<template>
  <AppLayout>
    <PageHeader
      eyebrow="Company workspace"
      title="Selected student"
      back-to="/company/selected-students"
      back-label="Selected"
    />

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />
    <StateMessage
      v-else-if="!placement"
      icon="fas fa-user"
      title="Record not found"
      description="This placement record may have been removed or you are not authorized to view it."
    />

    <template v-else>
      <DetailHero
        :name="placement.student_name"
        :email="placement.student_email"
        id-label="Drive"
        :id-value="placement.job_title || 'N/A'"
        avatar-icon="fas fa-user-graduate"
      />

      <InfoSection
        title="Placement Details"
        icon="fas fa-briefcase"
        :items="[
          { label: 'Company', value: placement.company_name },
          { label: 'Join date', value: formatDate(placement.join_date) },
          { label: 'Package (LPA)', value: placement.package_lpa },
        ]"
      />

      <div class="pp-panel mb-4">
        <h3 class="pp-section-title">
          <i class="fas fa-align-left" aria-hidden="true"></i>Cover letter
        </h3>
        <div class="pp-panel p-3 bg-light" style="white-space: pre-wrap">
          {{ placement.cover_letter || "No cover letter provided." }}
        </div>
      </div>

      <div class="pp-panel">
        <h3 class="pp-section-title">
          <i class="fas fa-user" aria-hidden="true"></i>Resume
        </h3>
        <a
          v-if="placement.resume_link"
          :href="placement.resume_link"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-pp-outline btn-sm"
          >View resume</a
        >
        <div v-else class="text-muted">No resume available.</div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import PageHeader from "../components/PageHeader.vue";
import DetailHero from "../components/DetailHero.vue";
import InfoSection from "../components/InfoSection.vue";
import StateMessage from "../components/StateMessage.vue";
import SkeletonBlock from "../components/SkeletonBlock.vue";
import http from "../api/http";

const route = useRoute();
const loading = ref(true);
const placement = ref(null);

onMounted(loadPlacement);

async function loadPlacement() {
  loading.value = true;
  try {
    const resp = await http.get("/api/v1/company/selected-students");
    const arr = resp.data.selected || [];
    placement.value = arr.find((p) => p.id === Number(route.params.id)) || null;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function formatDate(value) {
  return value
    ? new Date(value).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : "N/A";
}
</script>
